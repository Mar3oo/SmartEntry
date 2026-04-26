import easyocr
from typing import List, Dict, Any
from PIL.Image import Image
import numpy as np


class OCRExtractionError(Exception):
    pass


# Initialize once (important for performance)
reader = easyocr.Reader(['en'], gpu=False)


def extract(images: List[Image]) -> Dict[str, Any]:
    """
    Extract text from images using EasyOCR.

    Args:
        images (List[PIL.Image]): list of images

    Returns:
        dict: standardized extraction output
    """
    try:
        full_text = []
        blocks = []

        for page_idx, image in enumerate(images, start=1):

            image_np = np.array(image)
            results = reader.readtext(image_np)

            page_text_parts = []

            for (bbox, text, confidence) in results:
                page_text_parts.append(text)

                # bbox is 4 points → convert to [x1, y1, x2, y2]
                x_coords = [p[0] for p in bbox]
                y_coords = [p[1] for p in bbox]

                block = {
                    "text": text,
                    "bbox": [
                        min(x_coords),
                        min(y_coords),
                        max(x_coords),
                        max(y_coords)
                    ],
                    "page": page_idx
                }

                blocks.append(block)

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