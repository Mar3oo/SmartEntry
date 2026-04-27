from numpy import extract
import pdfplumber
from typing import Dict, Any, List


class PDFExtractionError(Exception):
    pass


class PDFPlumberService:
    def extract(self, file_path: str) -> Dict[str, Any]:
        try:
            full_text = []
            blocks: List[Dict[str, Any]] = []

            with pdfplumber.open(file_path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):

                    page_text = page.extract_text() or ""
                    full_text.append(page_text)

                    words = page.extract_words()

                    lines = {}
                    for word in words:
                        key = round(word["top"], 1)
                        lines.setdefault(key, []).append(word)

                    for line_words in lines.values():
                        line_words = sorted(line_words, key=lambda w: w["x0"])
                        line_text = " ".join(w["text"] for w in line_words)

                        x0 = min(w["x0"] for w in line_words)
                        top = min(w["top"] for w in line_words)
                        x1 = max(w["x1"] for w in line_words)
                        bottom = max(w["bottom"] for w in line_words)

                        blocks.append({
                            "text": line_text,
                            "bbox": [x0, top, x1, bottom],
                            "page": page_number
                        })

            return {
                "text": "\n".join(full_text),
                "blocks": blocks,
                "metadata": {
                    "source": "pdf",
                    "pages": len(full_text)
                }
            }

        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF: {str(e)}")

class PDFService:
    def __init__(self):
        self.service = PDFPlumberService()

    def extract(self, file_path: str) -> dict:
        return self.service.extract(file_path)