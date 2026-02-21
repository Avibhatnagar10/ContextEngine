import chromadb
from embeddings.embedding_model import generate_embedding

client = chromadb.HttpClient(host="localhost", port=8000)

collection = client.get_collection(name="documents")

def query_similar(text: str, n_results=3):
    query_embedding = generate_embedding(text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results