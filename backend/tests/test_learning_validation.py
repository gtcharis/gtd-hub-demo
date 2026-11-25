from io import BytesIO
from zipfile import ZipFile
import pytest
from fastapi import HTTPException
from app.api.learning_routes import _validate_external_url, _validate_file


def test_external_learning_links_require_https():
    assert _validate_external_url("https://example.org/guide") == "https://example.org/guide"
    for value in ("http://example.org", "file:///etc/passwd", "https://localhost/resource", "https://127.0.0.1/file", "https://user:pass@example.org"):
        with pytest.raises(HTTPException):
            _validate_external_url(value)


def test_pdf_upload_checks_signature_and_mime():
    assert _validate_file("guide.pdf", "application/pdf", b"%PDF-1.7\ncontent")[1] == "application/pdf"
    with pytest.raises(HTTPException):
        _validate_file("guide.pdf", "application/pdf", b"not a pdf")
    with pytest.raises(HTTPException):
        _validate_file("guide.exe", "application/octet-stream", b"MZ")


def _office_file(document_path: str) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr(document_path, "<document/>")
    return buffer.getvalue()


def test_docx_and_pptx_require_expected_package_entries():
    docx = _office_file("word/document.xml")
    pptx = _office_file("ppt/presentation.xml")
    assert _validate_file("guide.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", docx)[0] == ".docx"
    assert _validate_file("slides.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", pptx)[0] == ".pptx"
    with pytest.raises(HTTPException):
        _validate_file("wrong.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", pptx)


def test_upload_size_is_limited_to_ten_megabytes():
    with pytest.raises(HTTPException) as exc:
        _validate_file("large.pdf", "application/pdf", b"%PDF-" + b"x" * (10 * 1024 * 1024))
    assert exc.value.status_code == 413
