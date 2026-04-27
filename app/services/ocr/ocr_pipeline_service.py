from typing import Dict, Any
from app.services.pdf.pymupdf_service import convert_to_images
from app.services.ocr.easyocr_service import EasyOCRService
from app.services.vision.preprocessing import preprocess_image


class OCRPipelineService:
    def __init__(self):
        self.ocr_service = EasyOCRService()

    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Full OCR pipeline:
        PDF -> images -> OCR
        """

        images = convert_to_images(file_path)

        processed_images = [preprocess_image(img) for img in images]

        return self.ocr_service.extract(processed_images)