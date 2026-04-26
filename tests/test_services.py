import pytest
from app.services.detection.input_classifier import classify, InputClassifierError


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