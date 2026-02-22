import pdfplumber


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
    # Fix weird spacing like: N e x S t r e a m
    text = text.replace("\n", " ")
    text = " ".join(text.split())

    # Optional: Fix spaced characters
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")

    return text