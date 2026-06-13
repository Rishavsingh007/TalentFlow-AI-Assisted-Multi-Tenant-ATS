import logging
import os

from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _detect_mime(head: bytes) -> str | None:
    try:
        import magic

        return magic.from_buffer(head, mime=True)
    except (ImportError, OSError):
        logger.debug("libmagic unavailable; using header-based MIME detection")
        if head.startswith(b"%PDF"):
            return "application/pdf"
        if head.startswith(b"PK"):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return None


def validate_resume_upload(uploaded_file) -> None:
    if uploaded_file is None:
        raise ValidationError({"resume": "Resume file is required."})

    if uploaded_file.size > MAX_RESUME_SIZE:
        raise ValidationError({"resume": "Resume file must be 5 MB or smaller."})

    name = uploaded_file.name or ""
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError({"resume": "Only PDF and DOCX files are allowed."})

    head = uploaded_file.read(2048)
    uploaded_file.seek(0)

    mime = _detect_mime(head)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError({"resume": "Invalid file type. Only PDF and DOCX files are allowed."})
