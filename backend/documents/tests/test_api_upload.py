import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document


def _fake_pdf_bytes(text: str) -> bytes:
    """
    Делает минимальный PDF (1 страница) с текстом.
    pypdf извлекает текст из таких PDF корректно.
    """
    content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 60 >>
stream
BT
/F1 18 Tf
50 200 Td
({text}) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000061 00000 n
0000000116 00000 n
0000000240 00000 n
0000000350 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
420
%%EOF
"""
    return content.encode("latin-1", errors="ignore")


def _fake_docx_bytes(text: str) -> bytes:
    """
    Создаёт DOCX в памяти через python-docx.
    """
    from docx import Document as DocxDocument

    bio = io.BytesIO()
    d = DocxDocument()
    d.add_paragraph(text)
    d.save(bio)
    return bio.getvalue()


@pytest.mark.django_db
def test_upload_receipt_txt_sets_category_and_message(api_client, user):
    api_client.force_authenticate(user=user)

    content = "чек\nитого 1290\nфн 123\n".encode()
    upload = SimpleUploadedFile("chek.txt", content, content_type="text/plain")

    resp = api_client.post("/api/documents/", data={"file": upload}, format="multipart")

    assert resp.status_code == 201
    assert resp.data["category"] == "receipt"
    assert "чек" in resp.data["message"].lower()

    doc = Document.objects.get(id=resp.data["id"])
    assert doc.category == "receipt"
    assert doc.status == Document.Status.PROCESSED


@pytest.mark.django_db
def test_upload_contract_txt_sets_category_and_message(api_client, user):
    api_client.force_authenticate(user=user)

    content = "ДОГОВОР\nстороны\nпредмет договора\nсрок\n".encode()
    upload = SimpleUploadedFile("dogovor.txt", content, content_type="text/plain")

    resp = api_client.post("/api/documents/", data={"file": upload}, format="multipart")

    assert resp.status_code == 201
    assert resp.data["category"] == "contract"
    assert "договор" in resp.data["message"].lower()


@pytest.mark.django_db
def test_upload_unknown_txt_sets_other_category(api_client, user):
    api_client.force_authenticate(user=user)

    content = "просто текст без ключевых слов\n".encode()
    upload = SimpleUploadedFile("random.txt", content, content_type="text/plain")

    resp = api_client.post("/api/documents/", data={"file": upload}, format="multipart")

    assert resp.status_code == 201
    assert resp.data["category"] == "other"
    assert "неизвест" in resp.data["message"].lower()


def test_upload_contract_pdf(api_client, user):
    api_client.force_authenticate(user=user)

    pdf_bytes = _fake_pdf_bytes("ДОГОВОР")
    f = SimpleUploadedFile("dogovor.pdf", pdf_bytes, content_type="application/pdf")

    resp = api_client.post("/api/documents/", data={"file": f}, format="multipart")
    assert resp.status_code == 201
    assert resp.data["category"] == "contract"
    assert "договор" in resp.data["message"].lower()
    assert resp.data["status"] == "processed"


def test_upload_contract_docx(api_client, user):
    api_client.force_authenticate(user=user)

    docx_bytes = _fake_docx_bytes("ДОГОВОР")
    f = SimpleUploadedFile(
        "dogovor.docx",
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    resp = api_client.post("/api/documents/", data={"file": f}, format="multipart")
    assert resp.status_code == 201
    assert resp.data["category"] == "contract"
    assert "договор" in resp.data["message"].lower()
    assert resp.data["status"] == "processed"
