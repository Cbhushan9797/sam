import json
from io import BytesIO
import streamlit as st
import pandas as pd

from utils.df_utils import make_arrow_compatible, load_excel_dataframe_safe
from utils.api import (
    BASE_URL, DOWNLOAD_URL, EXECUTE_URL, EXECUTE_UPLOADED_URL, stream_chat
)

st.set_page_config(page_title="Test Automation Agent", page_icon="🤖", layout="centered")

try:
    st.image("../assets/logo.png", width=180)
except Exception:
    pass

st.title("Test Automation Agent")

# -------- State --------
if "goals" not in st.session_state:
    st.session_state.goals = {
        "started": {"done": False},
        "reading_excel": {"done": False},
        "generating_script": {"done": False},
        "saving_script": {"done": False},
        "done": {"done": False},
    }
if "streaming" not in st.session_state:
    st.session_state.streaming = False
if "final_done" not in st.session_state:
    st.session_state.final_done = False
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
    st.session_state.filename = None
    st.session_state.preview_clicked = False

goals = st.session_state.goals

tab1, tab2 = st.tabs(["Script Generation Agent", "Script Execution Agent"])
# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("Generate Playwright Script from Excel")
    col_u_left, col_u_right = st.columns([1, 1])

    with col_u_left:
        steps_file = st.file_uploader("Upload Manual steps (.txt or Excel)", type=["txt", "xls", "xlsx", "xlsb"], key="steps_file")
        if steps_file:
            if steps_file.name.endswith(".txt"):
                st.text_area("Steps Preview:", value=steps_file.getvalue().decode("utf-8"), height=150, disabled=True)
            else:
                try:
                    df = load_excel_dataframe_safe(steps_file.name, steps_file.getvalue())
                    df = make_arrow_compatible(df)
                    st.dataframe(df.head(10), width="stretch")
                except Exception as e:
                    st.error(f"Error reading steps: {e}")

    with col_u_right:
        data_file = st.file_uploader("Upload Test data (.txt or Excel)", type=["txt", "xls", "xlsx", "xlsb"], key="data_file")
        if data_file:
            if data_file.name.endswith(".txt"):
                st.text_area("Data Preview:", value=data_file.getvalue().decode("utf-8"), height=150, disabled=True)
            else:
                try:
                    df2 = load_excel_dataframe_safe(data_file.name, data_file.getvalue())
                    df2 = make_arrow_compatible(df2)
                    st.dataframe(df2.head(10), width="stretch")
                except Exception as e:
                    st.error(f"Error reading data: {e}")

    generate_btn = st.button("🚀 Generate Script", type="primary", key="gen_btn")

    if generate_btn:
        if not steps_file:
            st.warning("⚠️ Please upload the Manual steps file first.")
        else:
            st.session_state.streaming = True
            st.session_state.final_done = False
            for k in goals:
                goals[k]["done"] = False
            st.session_state.goals = goals

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("🎯 Goals")
        ph_started, ph_reading = st.empty(), st.empty()
        ph_generating, ph_saving = st.empty(), st.empty()
        ph_done = st.empty()

        ph_started.write("⭕ **Started**")
        ph_reading.write("⭕ **Reading Files**")
        ph_generating.write("⭕ **Generating Script**")
        ph_saving.write("⭕ **Saving Script**")
        ph_done.write("⭕ **Done**")

        def render_goals():
            ph_started.write("✅ **Started**" if goals["started"]["done"] else "⭕ **Started**")
            ph_reading.write("✅ **Reading Files**" if goals["reading_excel"]["done"] else "⭕ **Reading Files**")
            ph_generating.write("✅ **Generating Script**" if goals["generating_script"]["done"] else "⭕ **Generating Script**")
            ph_saving.write("✅ **Saving Script**" if goals["saving_script"]["done"] else "⭕ **Saving Script**")
            ph_done.write("✅ **Done**" if goals["done"]["done"] else "⭕ **Done**")

    with col_right:
        st.subheader("📜 Live Output")
        output_area = st.empty()

        if st.session_state.streaming:
            try:
                data_payload = {}
                files_payload = {}

                # Steps File
                s_name = steps_file.name.lower()
                s_ext = s_name.split(".")[-1]
                s_mime = "text/plain" if s_ext == "txt" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                files_payload["steps_file"] = (steps_file.name, steps_file.getvalue(), s_mime)

                # Data File
                if data_file:
                    d_name = data_file.name.lower()
                    d_ext = d_name.split(".")[-1]
                    d_mime = "text/plain" if d_ext == "txt" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    files_payload["data_file"] = (data_file.name, data_file.getvalue(), d_mime)

                streamed_text = ""

                for item in stream_chat(data_payload, files_payload):
                    if hasattr(item, "status_code"):
                        if item.status_code != 200:
                            st.error(f"Backend error: {item.text}")
                            st.session_state.streaming = False
                            break
                        continue

                    line = item
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="ignore")
                    
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        evt = json.loads(line)
                    except Exception:
                        streamed_text += line + "\n"
                        output_area.markdown(f"```\n{streamed_text}\n```")
                        continue

                    etype = evt.get("type")

                    if etype == "status":
                        label, state = evt.get("label"), evt.get("state")
                        if label in goals:
                            goals[label]["done"] = (state == "complete")
                        st.session_state.goals = goals
                        render_goals()

                    elif etype == "delta":
                        token = evt.get("text", "")
                        streamed_text += token
                        output_area.markdown(f"```{streamed_text}```")

                    elif etype == "final":
                        streamed_text += evt.get("text", "")
                        output_area.markdown(f"```{streamed_text}```")
                        goals["done"]["done"] = True
                        st.session_state.goals = goals
                        st.session_state.final_done = True
                        render_goals()

                    elif etype == "error":
                        st.error(evt.get("message", "Unknown error"))

            except Exception as e:
                import traceback
                st.session_state.streaming = False
                st.error(f"⚠️ Request failed: {e}")
                with st.expander("🔍 Debug Traceback"):
                    st.code(traceback.format_exc())

# ---------------- TAB 2 ----------------
with tab2:
    st.header("Execute Playwright Script")

    uploaded_script = st.file_uploader("Upload Playwright test file", type=["js", "ts"], key="uploaded_script_simple")

    if st.button("⚙️ Execute Script", type="primary"):
        if not uploaded_script:
            st.warning("Please upload a script first.")
        else:
            with st.spinner("Executing script..."):
                import requests
                files = {
                    "script": (uploaded_script.name, uploaded_script.getvalue(), "application/javascript")
                }
                res = requests.post(EXECUTE_UPLOADED_URL, files=files, timeout=600)

                if res.status_code != 200:
                    st.error(f"Execution failed: {res.text}")
                else:
                    result = res.json()
                    st.success("Execution completed")
                    st.subheader("Stdout")
                    st.code(result.get("stdout", ""), language="bash")
                    st.subheader("Stderr")
                    st.code(result.get("stderr", ""), language="bash")