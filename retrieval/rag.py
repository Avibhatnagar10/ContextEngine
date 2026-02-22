import ollama
from retrieval.query import query_similar

def generate_rag_answer(question: str):

    # 1️⃣ Retrieve top relevant chunks
    results = query_similar(question, n_results=5)

    documents = results.get("documents", [[]])[0]

    # 2️⃣ Build context
    context = "\n\n".join(documents)

    prompt = f"""
You are an AI assistant.
Answer the question strictly using the provided context.

Context:
{context}

Question:
{question}

Answer:
"""

    # 3️⃣ Generate answer using Ollama LLM
    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "answer": response["message"]["content"],
        "context_used": documents
    }