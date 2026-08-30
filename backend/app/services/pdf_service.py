import re
import pymupdf as fitz
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
    """Clean up common PDF extraction artifacts."""

    # Remove NUL characters (PostgreSQL can't store these)
    text = text.replace('\x00', '')

    # Remove excessive whitespace (multiple spaces/tabs -> single space)
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove excessive blank lines (3+ newlines -> 2 newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove common page-number-only lines (e.g. a line that's just "12" or "Page 12")
    text = re.sub(r'\n\s*(Page\s*)?\d{1,4}\s*\n', '\n', text)

    # Fix hyphenated words broken across lines (e.g. "informa-\ntion" -> "information")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Remove lines that are just repeated copyright/footer boilerplate
    text = re.sub(r'©\d{4}.*?Linguistics\n?', '', text)

    text = text.strip()

    return text


def extract_text(file_path: str) -> str:
    """Try PyMuPDF first; fall back to pdfplumber if the result looks empty/too short."""
    text = extract_text_pymupdf(file_path)

    if len(text) < 50:
        text = extract_text_pdfplumber(file_path)

    text = clean_text(text)

    return text