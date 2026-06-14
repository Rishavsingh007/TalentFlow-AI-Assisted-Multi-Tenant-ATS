import os


class ResumeParseError(Exception):
    pass


def extract_text(resume_path: str) -> str:
    if not resume_path or not os.path.isfile(resume_path):
        raise ResumeParseError(f"Resume file not found: {resume_path}")

    ext = os.path.splitext(resume_path)[1].lower()
    if ext == ".pdf":
        text = _extract_pdf_text(resume_path)
    elif ext == ".docx":
        text = _extract_docx_text(resume_path)
    else:
        raise ResumeParseError(f"Unsupported resume format: {ext}")

    text = text.strip()
    if not text:
        raise ResumeParseError("No text could be extracted from resume")

    return text


def _extract_pdf_text(resume_path: str) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(resume_path)
        parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
        return "\n".join(parts)
    except PdfReadError as exc:
        raise ResumeParseError(f"Invalid or corrupted PDF: {exc}") from exc


def _extract_docx_text(resume_path: str) -> str:
    from docx import Document
    from docx.opc.exceptions import PackageNotFoundError

    try:
        document = Document(resume_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text)
    except (PackageNotFoundError, ValueError) as exc:
        raise ResumeParseError(f"Invalid or corrupted DOCX: {exc}") from exc
