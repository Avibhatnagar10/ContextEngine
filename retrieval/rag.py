import ollama
from retrieval.query import query_similar


def generate_answer(question: str):

    # 1️⃣ Try retrieving relevant chunks
    results = query_similar(question, n_results=5)
    documents = results.get("documents", [[]])[0]

    # 2️⃣ If documents found → RAG mode
    if documents and any(doc.strip() for doc in documents):

        context = "\n\n".join(documents)

        prompt = f"""
You are an AI assistant.
Answer the question strictly using the provided context.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{question}

Answer:
"""

        response = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "mode": "rag",
            "answer": response["message"]["content"],
            "context_used": documents
        }

    # 3️⃣ If nothing retrieved → normal chat
    else:
        response = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": question}]
        )

        return {
            "mode": "normal",
            "answer": response["message"]["content"],
            "context_used": []
        }