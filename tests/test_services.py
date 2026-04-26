import pytest
from app.services.detection.input_classifier import classify, InputClassifierError
# from app.services.pdf.pdfplumber_service import extract as pdf_extract
from app.services.pdf.pymupdf_service import convert_to_images
# from app.services.ocr.easyocr_service import extract as ocr_extract
from app.services.pdf.pdfplumber_service import PDFPlumberService
from app.services.ocr.easyocr_service import EasyOCRService
from app.services.ocr.ocr_pipeline_service import OCRPipelineService
from app.services.vision.preprocessing import preprocess_image


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
    service = PDFPlumberService()
    file_path = "tests/fixtures/sample_invoice.pdf"

    result = service.extract(file_path)

    assert "text" in result
    assert "blocks" in result
    assert "metadata" in result

    assert isinstance(result["text"], str)
    assert isinstance(result["blocks"], list)
    assert result["metadata"]["source"] == "pdf"
    
def test_pymupdf_convert_to_images():
    file_path = "tests/fixtures/sample_invoice.pdf"

    images = convert_to_images(file_path)

    assert isinstance(images, list)
    assert len(images) > 0

    # check first item is image
    from PIL.Image import Image
    assert isinstance(images[0], Image)

def test_easyocr_extract():
    service = EasyOCRService()
    file_path = "tests/fixtures/sample_invoice.pdf"

    images = convert_to_images(file_path)
    result = service.extract(images)

    assert "text" in result
    assert "blocks" in result
    assert "metadata" in result

    assert isinstance(result["text"], str)
    assert isinstance(result["blocks"], list)
    assert result["metadata"]["source"] == "ocr"

def test_ocr_pipeline_service():
    service = OCRPipelineService()

    file_path = "tests/fixtures/sample_invoice.pdf"
    result = service.extract(file_path)

    assert "text" in result
    assert "blocks" in result
    assert "metadata" in result

    assert result["metadata"]["source"] == "ocr"

def test_preprocessing():
    file_path = "tests/fixtures/sample_invoice.pdf"

    images = convert_to_images(file_path)
    processed = preprocess_image(images[0])

    from PIL.Image import Image
    assert isinstance(processed, Image)