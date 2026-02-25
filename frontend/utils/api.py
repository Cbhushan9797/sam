import os
import requests

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

BASE_URL = f"{BACKEND_BASE_URL}/api/chat"
DOWNLOAD_URL = f"{BACKEND_BASE_URL}/download"
EXECUTE_URL = f"{BACKEND_BASE_URL}/api/execute"
EXECUTE_UPLOADED_URL = f"{BACKEND_BASE_URL}/api/execute-uploaded"

def stream_chat(data: dict, files: dict):
    """
    Yields:
      - the initial Response object once
      - each line from the backend as raw bytes
    """
    res = requests.post(BASE_URL, data=data, files=files, stream=True, timeout=(15, 3600))
    yield res

    if res.status_code == 200:
        # We handle decoding manually in the frontend for maximum control
        for line in res.iter_lines(decode_unicode=False, delimiter=b"\n"):
            if line:
                yield line