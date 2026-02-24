#ContextEngine\retrieval\query.py
import chromadb
from embeddings.embedding_model import generate_embedding

# Same persistent client path
client = chromadb.PersistentClient(path="./data")

collection = client.get_or_create_collection(
    name="documents"
)

def query_similar(text: str, n_results=5):
    query_embedding = generate_embedding(text)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"]
        )
        return results
    except Exception as e:
        return {
            "documents": [[]],
            "distances": [[]]
        }

    return results