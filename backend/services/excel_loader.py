import os
import io
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def _engine_for_ext(filename: str) -> str | None:
    ext = (os.path.splitext(filename)[1] or "").lower()
    if ext == ".xlsx":
        return "openpyxl"
    if ext == ".xls":
        return "xlrd"  # requires xlrd==1.2.0
    if ext == ".xlsb":
        return "pyxlsb"
    return None

def read_excel_bytes_to_csv(content, filename: str) -> str:
    """
    Safely read Excel content and return CSV string.
    Forcefully handles both bytes and strings to avoid 'bytes-like object required' errors.
    """
    if content is None:
        return ""

    # Ensure we have bytes
    if isinstance(content, str):
        logger.warning(f"Excel loader received string for {filename}, encoding to bytes.")
        data = content.encode('utf-8', errors='ignore')
    elif isinstance(content, bytes):
        data = content
    else:
        # If it's some other object (like a file stream), try to read it
        try:
            data = content.read()
            if isinstance(data, str):
                data = data.encode('utf-8')
        except Exception:
            logger.error(f"Could not convert {type(content)} to bytes.")
            raise TypeError(f"Expected bytes or string, got {type(content)}")

    engine = _engine_for_ext(filename or "")
    bio = io.BytesIO(data)

    try:
        # Try with the suggested engine
        if engine:
            df = pd.read_excel(bio, engine=engine)
        else:
            df = pd.read_excel(bio)
    except Exception as e:
        logger.warning(f"Failed to read Excel with engine {engine}: {e}. Trying fallback.")
        bio.seek(0)
        try:
            # Universal fallback
            df = pd.read_excel(bio)
        except Exception as fallback_e:
            logger.error(f"Excel fallback failed: {fallback_e}")
            raise

    return df.to_csv(index=False)