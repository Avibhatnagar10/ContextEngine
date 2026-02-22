from fastapi import APIRouter, UploadFile, File
from ingestion.ingest import ingest_document, ingest_file
from retrieval.query import query_similar
from retrieval.rag import generate_rag_answer
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/ingest")
def ingest(id: str, text: str):
    return ingest_document(id, text)


@router.get("/query")
def query(q: str):
    return query_similar(q)


@router.get("/rag")
def rag(q: str):
    return generate_rag_answer(q)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return ingest_file(file_path)

