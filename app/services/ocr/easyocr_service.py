import easyocr
import numpy as np
from app.services.pdf.pymupdf_service import convert_to_images



class OCRExtractionError(Exception):
    pass


class EasyOCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract(self, file_path: str) -> dict:

        images = convert_to_images(file_path)

        full_text = []
        blocks = []

        for page_idx, image in enumerate(images, start=1):

            image_np = np.array(image)
            results = self.reader.readtext(image_np)

            page_text_parts = []

            for (bbox, text, confidence) in results:
                page_text_parts.append(text)

                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]

                blocks.append({
                    "text": text,
                    "bbox": [
                        min(x_coords),
                        min(y_coords),
                        max(x_coords),
                        max(y_coords)
                    ],
                    "page": page_idx
                })

            full_text.append(" ".join(page_text_parts))

        return {
            "text": "\n".join(full_text),
            "blocks": blocks,
            "metadata": {
                "source": "ocr",
                "pages": len(images)  # ✅ صح
            }
        }
class OCRService:
    def __init__(self):
        self.service = EasyOCRService()

    def extract(self, file_path: str) -> dict:
        return self.service.extract(file_path)