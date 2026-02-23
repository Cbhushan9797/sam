import os
from io import BytesIO
import pandas as pd

def make_arrow_compatible(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        s = df[col]

        if pd.api.types.is_numeric_dtype(s):
            if s.dropna().apply(lambda x: float(x).is_integer()).all():
                df[col] = s.astype("Int64")
            else:
                df[col] = pd.to_numeric(s, errors="coerce")
            continue

        if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
            numeric_try = pd.to_numeric(s, errors="coerce")
            if numeric_try.notna().mean() >= 0.7:
                df[col] = numeric_try
                if df[col].dropna().apply(lambda x: float(x).is_integer()).all():
                    df[col] = df[col].astype("Int64")
            else:
                df[col] = s.astype("string")
            continue

        df[col] = s.astype("string")

    return df


def load_excel_dataframe_safe(name: str, raw_bytes: bytes) -> pd.DataFrame:
    """Fresh BytesIO per attempt + engine selection."""
    ext = (os.path.splitext(name)[1] or "").lower()

    def fresh_io():
        bio = BytesIO(raw_bytes)
        bio.seek(0)
        return bio

    try:
        if ext == ".xlsx":
            return pd.read_excel(fresh_io(), sheet_name=0, engine="openpyxl")
        elif ext == ".xls":
            return pd.read_excel(fresh_io(), sheet_name=0, engine="xlrd")
        elif ext == ".xlsb":
            return pd.read_excel(fresh_io(), sheet_name=0, engine="pyxlsb")
        return pd.read_excel(fresh_io(), sheet_name=0)

    except Exception:
        try:
            return pd.read_excel(fresh_io(), sheet_name=0)
        except Exception:
            if ext == ".xlsx":
                from openpyxl import load_workbook
                wb = load_workbook(filename=fresh_io(), read_only=True, data_only=True)
                ws = wb.worksheets[0]
                rows = list(ws.values)
                header = [str(h) if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
                return pd.DataFrame(rows[1:], columns=header)
            raise

    return pd.read_excel(fresh_io(), sheet_name=0)