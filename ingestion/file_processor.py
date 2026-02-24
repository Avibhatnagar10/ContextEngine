import pdfplumber
import re

def extract_text_from_pdf(file_path: str):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return clean_text(text)


def extract_text_from_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return clean_text(f.read())


def clean_text(text: str):
    # Normalize Windows line endings
    text = text.replace("\r\n", "\n")

    # Remove trailing spaces
    text = "\n".join(line.strip() for line in text.split("\n"))

    # Collapse multiple empty lines into one
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Fix spacing around punctuation
    text = re.sub(r"\s+([.,!?])", r"\1", text)

    return text.strip()