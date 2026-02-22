import chromadb
from embeddings.embedding_model import generate_embedding
from ingestion.chunker import chunk_text

client = chromadb.PersistentClient(path="./data")
client.delete_collection("documents")

collection = client.get_or_create_collection(
    name="documents"
)

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
        metadatas=metadatas
    )

    return {"status": "stored", "chunks": len(chunks)}