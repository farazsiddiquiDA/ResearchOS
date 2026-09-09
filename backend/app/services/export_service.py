from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import io

def generate_paper_excel(paper, extracted) -> io.BytesIO:
    """Generate an Excel file with one paper's summary."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Paper Summary"

    # Header row
    ws["A1"] = "Field"
    ws["B1"] = "Value"
    ws["A1"].font = Font(bold=True)
    ws["B1"].font = Font(bold=True)

    rows = [
        ("Title", paper.title or "Not specified"),
        ("Filename", paper.filename),
        ("Research Problem", extracted.research_problem),
        ("Method Used", extracted.method_used),
        ("Dataset", extracted.dataset),
        ("Algorithm", extracted.algorithm),
        ("Results", extracted.results),
        ("Advantage", extracted.advantage),
        ("Limitation", extracted.limitation),
        ("Future Scope", extracted.future_scope),
        ("Narrative Summary", extracted.narrative_summary),
    ]

    for i, (field, value) in enumerate(rows, start=2):
        ws[f"A{i}"] = field
        ws[f"B{i}"] = value
        ws[f"B{i}"].alignment = Alignment(wrap_text=True, vertical="top")

    # Widen columns for readability
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 80

    # Save to an in-memory buffer instead of disk
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer