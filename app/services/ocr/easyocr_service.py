import easyocr
import numpy as np
from typing import List, Dict, Any
from PIL.Image import Image


class OCRExtractionError(Exception):
    pass


class EasyOCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract(self, images: List[Image]) -> Dict[str, Any]:
        try:
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
                    "pages": len(images)
                }
            }

        except Exception as e:
            raise OCRExtractionError(f"OCR extraction failed: {str(e)}")