import fitz
import pdfplumber

def extract_text_pymupdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_pdfplumber(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def clean_text(text: str) -> str:
    """Remove null bytes and other characters Postgres can't store."""
    return text.replace("\x00", "")

def extract_text(file_path: str) -> str:
    text = extract_text_pymupdf(file_path)

    if len(text) < 50:
        text = extract_text_pdfplumber(file_path)

    return clean_text(text)