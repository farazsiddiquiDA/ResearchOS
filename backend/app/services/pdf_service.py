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

# Common section heading patterns seen across most papers
SECTION_PATTERNS = [
    "abstract",
    "introduction",
    "related work",
    "background",
    "methodology",
    "method",
    "methods",
    "approach",
    "experiments",
    "experimental setup",
    "results",
    "results and discussion",
    "discussion",
    "evaluation",
    "conclusion",
    "conclusions",
    "future work",
    "limitations",
    "references"
]

def split_into_sections(text: str) -> dict:
    """Split cleaned text into sections based on common heading patterns."""
    lines = text.split("\n")
    sections = {}
    current_section = "preamble"  # anything before the first recognized heading
    current_content = []

    for line in lines:
        stripped = line.strip()
        # Remove leading numbers like "1." or "2.1" from potential headings
        heading_candidate = re.sub(r'^\d+(\.\d+)*\.?\s*', '', stripped).lower()

        # A line counts as a heading if it's short and matches a known section name
        is_heading = (
            len(stripped) < 60
            and heading_candidate in SECTION_PATTERNS
        )

        if is_heading:
            # Save the previous section before starting a new one
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = heading_candidate
            current_content = []
        else:
            current_content.append(line)

    # Save the last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()

    return sections

def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list[str]:
    """Split long text into overlapping chunks so it fits LLM context limits."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_chars - overlap  # move forward, but overlap slightly with the previous chunk

    return chunks
def extract_basic_metadata(text: str) -> dict:
    """Best-effort extraction of title from the start of the raw text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    title = None
    for line in lines[:10]:  # title is almost always in the first few lines
        # Skip lines that look like conference/journal boilerplate
        if any(skip in line.lower() for skip in ["proceedings", "pages", "©", "association for"]):
            continue
        # A reasonable title: not too short, not too long, no weird symbols dominating
        if 15 < len(line) < 200:
            title = line
            break

    return {"title": title}