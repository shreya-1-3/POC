from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
import shutil
from datetime import datetime
from database import engine
from excel_parser import process_excel
from schema import get_schema
from llm import generate_sql, summarize_result

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = []
uploaded_tables = []


@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        return {"error": "Only .xlsx files allowed"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tables = process_excel(file_path, engine)

    uploaded_tables.clear()
    uploaded_tables.extend(tables)

    uploaded_files.append({
        "filename": file.filename,
        "tables": tables,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return {
        "message": "Upload successful",
        "tables": tables
    }


@app.get("/preview")
def preview_table(table: str):
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT * FROM {table} LIMIT 10")
            ).fetchall()

        return {
            "table": table,
            "data": [dict(r._mapping) for r in rows]
        }
    except Exception as e:
        return {
            "error": "Failed to load preview",
            "details": str(e)
        }



@app.get("/dashboard")
def dashboard():
    if not uploaded_tables:
        return {
            "kpis": {},
            "files": uploaded_files,
            "preview": []
        }

    table = uploaded_tables[0]

    with engine.connect() as conn:
        row_count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()

        preview_rows = conn.execute(
            text(f"SELECT * FROM {table} LIMIT 10")
        ).fetchall()

    return {
        "kpis": {
            "Total Rows": row_count
        },
        "files": uploaded_files,
        "preview": [dict(r._mapping) for r in preview_rows]
    }



@app.post("/chat")
def chat(question: str):
    print("CHAT API HIT:", question)
    if not uploaded_tables:
        return {
            "error": "No data uploaded",
            "message": "Upload an Excel file first"
        }

    schema = get_schema(engine)

    try:
        sql = generate_sql(question, schema)
    except Exception as e:
        return {
            "error": "LLM failed to generate SQL",
            "details": str(e)
        }

    try:
        with engine.connect() as conn:
            rows = conn.execute(text(sql)).fetchall()
    except Exception as e:
        return {
            "error": "SQL execution failed",
            "sql": sql,
            "details": str(e)
        }

    return {
        "sql": sql,
        "summary": summarize_result(question, rows),
        "data": [dict(r._mapping) for r in rows]
    }
