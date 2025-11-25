from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO
import json
import pandas as pd
import docx

app = FastAPI()


def excel_to_text(content: bytes) -> str:
    df = pd.read_excel(BytesIO(content))
    # You can change to to_string() if you prefer a table view
    return df.to_csv(index=False)


def csv_to_text(content: bytes) -> str:
    return content.decode(errors="ignore")


def json_to_text(content: bytes) -> str:
    obj = json.loads(content.decode(errors="ignore"))
    return json.dumps(obj, indent=2, ensure_ascii=False)


def docx_to_text(content: bytes) -> str:
    document = docx.Document(BytesIO(content))
    return "\n".join(p.text for p in document.paragraphs)


@app.post("/file-to-text")
async def file_to_text(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or ""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    try:
        if ext in {"xlsx", "xls"}:
            text = excel_to_text(content)
        elif ext == "csv":
            text = csv_to_text(content)
        elif ext == "json":
            text = json_to_text(content)
        elif ext == "docx":
            text = docx_to_text(content)
        else:
            # Fallback: treat as plain text
            text = content.decode(errors="ignore")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {ex}")

    return {
        "filename": filename,
        "extension": ext,
        "text": text,
    }
