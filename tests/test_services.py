import pytest
from app.services.detection.input_classifier import classify, InputClassifierError
from app.services.pdf.pdfplumber_service import extract


def test_classify_pdf(tmp_path):
    file = tmp_path / "test.pdf"
    file.write_text("dummy")
    assert classify(str(file)) == "pdf"


def test_classify_image(tmp_path):
    file = tmp_path / "test.jpg"
    file.write_text("dummy")
    assert classify(str(file)) == "image"


def test_classify_unsupported(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("dummy")
    with pytest.raises(InputClassifierError):
        classify(str(file))


def test_classify_nonexistent():
    with pytest.raises(InputClassifierError):
        classify("non_existent_file.pdf")
        

def test_pdfplumber_extract():
    file_path = "tests/fixtures/sample_invoice.pdf"

    result = extract(file_path)

    assert "text" in result
    assert "blocks" in result
    assert "metadata" in result

    assert isinstance(result["text"], str)
    assert isinstance(result["blocks"], list)
    assert result["metadata"]["source"] == "pdf"