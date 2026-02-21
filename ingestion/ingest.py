import chromadb
from chromadb.config import Settings
from embeddings.embedding_model import generate_embedding

client = chromadb.HttpClient(host="localhost", port=8000)

collection = client.get_or_create_collection(
    name="documents"
)

def ingest_document(doc_id: str, text: str):
    embedding = generate_embedding(text)

    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding]
    )