def chunk_text(text: str, max_chars=800):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks