import json
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse, FileResponse

from backend.services import excel_loader, agent, files, execution
import backend.config as config

app = FastAPI()

def to_bytes(data):
    """Universal converter to ensure we always yield bytes."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode("utf-8")
    return json.dumps(data).encode("utf-8")

@app.post("/api/chat")
async def chat(
    steps_file: UploadFile = File(...),
    data_file: Optional[UploadFile] = File(None),
):
    if steps_file is None:
        raise HTTPException(status_code=400, detail="Steps file is required.")

    async def stream_generator():
        try:
            yield to_bytes({"type": "status", "label": "started", "state": "complete", "percent": 5}) + b"\n"
            
            # Read Steps File
            yield to_bytes({"type": "status", "label": "reading_excel", "state": "begin", "percent": 8}) + b"\n"
            try:
                steps_content = await steps_file.read()
                fname = steps_file.filename.lower()
                if fname.endswith(".txt"):
                    steps_text = steps_content.decode("utf-8")
                else:
                    steps_text = excel_loader.read_excel_bytes_to_csv(steps_content, steps_file.filename)
                
                yield to_bytes({"type": "status", "label": "reading_excel", "state": "complete", "percent": 10}) + b"\n"
            except Exception as e:
                yield to_bytes({"type": "status", "label": "reading_excel", "state": "fail"}) + b"\n"
                yield to_bytes({"type": "error", "message": f"Steps File Error: {str(e)}"}) + b"\n"
                return

            # Read Data File (Optional)
            data_text = "None"
            if data_file and (data_file.filename or "").strip():
                yield to_bytes({"type": "status", "label": "reading_data_excel", "state": "begin"}) + b"\n"
                try:
                    data_content = await data_file.read()
                    dfname = data_file.filename.lower()
                    if dfname.endswith(".txt"):
                        data_text = data_content.decode("utf-8")
                    else:
                        data_text = excel_loader.read_excel_bytes_to_csv(data_content, data_file.filename)
                    
                    yield to_bytes({"type": "status", "label": "reading_data_excel", "state": "complete"}) + b"\n"
                except Exception as e:
                    yield to_bytes({"type": "error", "message": f"Data File Error: {str(e)}"}) + b"\n"
                    return

            prompt = f"Steps:\n{steps_text}\n\nTest Data:\n{data_text}"

            async for line in agent.orchestrator(prompt):
                # line is already an NDJSON string from agent.py
                yield to_bytes(line)

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            # Log it to console for us to see in the terminal
            print(f"CRITICAL ERROR: {error_trace}")
            yield to_bytes({"type": "error", "message": str(e)}) + b"\n"

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

@app.get("/download")
def download_file():
    tests_dir: Path = config.TESTS_DIR
    if not tests_dir.exists():
        raise HTTPException(status_code=404, detail="No tests found")
    files_list = sorted([p for p in tests_dir.iterdir() if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not files_list:
        raise HTTPException(status_code=404, detail="No files")
    return FileResponse(files_list[0], filename=files_list[0].name)

@app.post("/api/execute")
async def execute_saved_script():
    return {"status": "ok", "result": execution.execute_script()}

@app.post("/api/execute-uploaded")
async def upload_and_execute(script: UploadFile = File(...)):
    content = await script.read()
    files.save_uploaded_as_canonical_test(content, script.filename)
    return {"status": "ok", "execute": execution.execute_uploaded_script()}