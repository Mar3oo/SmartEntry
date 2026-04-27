import fitz  # PyMuPDF
from typing import List
from PIL import Image
import io


class PDFToImageError(Exception):
    pass


def convert_to_images(file_path: str) -> List[Image.Image]:
    """
    Convert PDF pages to images.

    Args:
        file_path (str): Path to PDF

    Returns:
        List[PIL.Image]: list of page images
    """
    try:
        images: List[Image.Image] = []

        doc = fitz.open(file_path)

        for page_index in range(len(doc)):
            page = doc[page_index]

            pix = page.get_pixmap()

            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))

            images.append(image)

        doc.close()

        return images

    except Exception as e:
        raise PDFToImageError(f"Failed to convert PDF to images: {str(e)}")