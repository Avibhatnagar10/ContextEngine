from fastapi import APIRouter
from ingestion.ingest import ingest_document
from retrieval.query import query_similar
from retrieval.rag import generate_rag_answer

router = APIRouter()

@router.post("/ingest")
def ingest(id: str, text: str):
    ingest_document(id, text)
    return {"status": "stored"}

@router.get("/query")
def query(q: str):
    return query_similar(q)

@router.get("/rag")
def rag(q: str):
    return generate_rag_answer(q)