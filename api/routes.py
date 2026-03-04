from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ingestion.ingest import ingest_document, ingest_file
from ingestion.ingest import collection
from retrieval.query import query_similar
from retrieval.rag import generate_answer
from auth.dependencies import get_current_user
from auth.roles import require_roles
from sqlalchemy.orm import Session
from db.database import get_db

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


# Ingest raw text
@router.post("/ingest")
def ingest(
    data: IngestRequest,
    user=Depends(require_roles("admin", "user"))
):
    return ingest_document(data.id, data.text)


# Current logged in user
@router.get("/auth/me")
def get_me(user=Depends(get_current_user)):
    return {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role
    }


# Vector search
@router.get("/query")
def query(
    q: str,
    user=Depends(get_current_user)
):
    return query_similar(q)


# RAG answer
@router.get("/rag")
def rag(
    q: str,
    user=Depends(get_current_user)
):
    return generate_answer(q)


# Upload file and ingest
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(require_roles("admin", "user"))
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return ingest_file(file_path)


# List documents
@router.get("/documents")
def get_documents(user=Depends(get_current_user)):

    results = collection.get()

    sources = set()

    for meta in results.get("metadatas", []):
        if meta and "source" in meta:
            sources.add(meta["source"])

    return [{"name": source} for source in sources]


# Delete document (admin only)
@router.delete("/documents/{filename}")
def delete_document(
    filename: str,
    user=Depends(require_roles("admin"))
):

    try:

        collection.delete(where={"source": filename})

        file_path = os.path.join(UPLOAD_DIR, filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        return {"message": f"{filename} deleted successfully"}

    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")


# Chroma health
@router.get("/health/chroma")
def chroma_health():

    try:
        response = requests.get(
            "http://localhost:8001/api/v2/heartbeat",
            timeout=10
        )

        if response.status_code == 200:
            return {"status": "active"}

    except Exception:
        pass

    return {"status": "offline"}