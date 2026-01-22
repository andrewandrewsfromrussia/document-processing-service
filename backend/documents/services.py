from __future__ import annotations

from io import BytesIO
from pathlib import Path


def detect_category(filename: str, text: str | None) -> tuple[str, str]:
    """
    Returns: (category_code, message)
    category_code in: receipt/contract/invoice/act/other
    """
    name = (filename or "").casefold()
    body = (text or "").casefold()

    def has_any(keys: list[str]) -> bool:
        return any(k in name or k in body for k in keys)

    # чек
    if has_any(["чек", "chek", "kassa", "итого", "кассир", "фиск", "фн", "фд", "офд"]):
        return "receipt", "Загружен чек"

    # договор (включая транслит/англ. варианты)
    if has_any(
        ["договор", "dogovor", "contract", "agreement", "стороны", "предмет", "срок"]
    ):
        return "contract", "Загружен договор"

    # счёт
    if has_any(["счет", "счёт", "schet", "invoice", "оплат", "инн", "кпп", "р/с"]):
        return "invoice", "Загружен счёт"

    # акт
    if has_any(
        [
            "акт",
            "act",
            "выполненных работ",
            "приема-передачи",
            "приёма-передачи",
            "оказанных услуг",
        ]
    ):
        return "act", "Загружен акт"

    return "other", "Загружен неизвестный документ"


def extract_text_from_upload(file_obj) -> str:
    """
    Extract text from:
    - .txt/.csv: decode with fallback
    - .pdf: pypdf
    - .docx: python-docx
    Otherwise: empty string
    """
    name = getattr(file_obj, "name", "") or ""
    ext = Path(name).suffix.lower()

    try:
        if hasattr(file_obj, "open"):
            file_obj.open("rb")
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        data: bytes = file_obj.read()
    finally:
        if hasattr(file_obj, "seek"):
            try:
                file_obj.seek(0)
            except Exception:
                pass

    if not data:
        return ""

    if ext in {".txt", ".csv"}:
        for enc in ("utf-8", "utf-8-sig", "cp1251"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()

    if ext == ".docx":
        from docx import Document as DocxDocument

        doc = DocxDocument(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()

    return ""
