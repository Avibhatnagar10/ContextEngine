#ContextEngine\ingestion\ingest.py
import os
import chromadb
from embeddings.embedding_model import generate_embedding
from ingestion.chunker import chunk_text
from ingestion.file_processor import (
    extract_text_from_pdf,
    extract_text_from_txt,
)

# Persistent local storage
client = chromadb.PersistentClient(path="./data")
# client.delete_collection("documents")

collection = client.get_or_create_collection(
    name="documents"
)


# 🔹 1. Ingest raw text
def ingest_document(doc_id: str, text: str):
    
    chunks = chunk_text(text)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        embedding = generate_embedding(chunk)

        ids.append(chunk_id)
        documents.append(chunk)
        embeddings.append(embedding)
        metadatas.append({"source": doc_id})

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {"status": "stored", "chunks": len(chunks)}


# 🔹 2. Ingest file (PDF / TXT)
def ingest_file(file_path: str):
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".txt"):
        text = extract_text_from_txt(file_path)
    else:
        return {"error": "Unsupported file type"}

    file_name = os.path.basename(file_path)

    return ingest_document(file_name, text)