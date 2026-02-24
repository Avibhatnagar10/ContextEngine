from fastapi import APIRouter, UploadFile, File, HTTPException
from ingestion.ingest import ingest_document, ingest_file
from ingestion.ingest import collection
from retrieval.query import query_similar
from retrieval.rag import generate_answer
import os
import shutil
import requests
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestRequest(BaseModel):
    id: str
    text: str
@router.post("/ingest")
def ingest(data: IngestRequest):
    return ingest_document(data.id, data.text)
    
@router.get("/health/chroma")
def chroma_health():
    try:
        response = requests.get("http://localhost:8001/api/v2/heartbeat", timeout=25)
        if response.status_code == 200:
            return {"status": "active"}
    except Exception:
        pass

    return {"status": "offline"}

@router.get("/query")
def query(q: str):
    return query_similar(q)


@router.get("/rag")
def rag(q: str):
    return generate_answer(q)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return ingest_file(file_path)

@router.get("/documents")
def get_documents():
    results = collection.get()

    sources = set()
    for meta in results.get("metadatas", []):
        if meta and "source" in meta:
            sources.add(meta["source"])

    return [{"name": source} for source in sources]

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    try:
        # 1️⃣ Delete from Chroma using metadata
        collection.delete(where={"source": filename})

        # 2️⃣ Delete physical file
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return {"message": f"{filename} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

