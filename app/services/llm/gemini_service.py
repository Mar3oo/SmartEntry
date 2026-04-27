import os
import json
from typing import Dict, Any, Optional
from PIL import Image

import google.generativeai as genai


class GeminiServiceError(Exception):
    pass


class GeminiService:
    def __init__(self, model: str = "gemini-1.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
        else:
            self.model = None

    def _build_prompt(self, ocr_text: Optional[str]) -> str:
        return f"""
You are an invoice extraction system.

Extract structured invoice data from the provided image.

Return ONLY valid JSON with this schema:

{{
  "supplier": null,
  "customer": null,
  "invoice": {{
    "invoice_number": string | null,
    "invoice_date": string | null
  }},
  "items": [
    {{
      "description": string | null,
      "quantity": number | null,
      "unit_price": number | null,
      "total_price": number | null
    }}
  ],
  "totals": {{
    "total": number | null
  }},
  "currency": string | null,
  "extra_fields": {{}}
}}

Rules:
- Output ONLY JSON
- Use null for missing fields
- Numbers must be numeric

OCR Context (optional):
{ocr_text if ocr_text else "None"}
"""

    def extract(self, file_path: str, ocr_text: Optional[str] = None) -> Dict[str, Any]:
        if self.model is None:
            raise GeminiServiceError("Gemini client not initialized (missing API key)")

        try:
            image = Image.open(file_path)

            prompt = self._build_prompt(ocr_text)

            response = self.model.generate_content([prompt, image])

            content = response.text.strip()

            return json.loads(content)

        except Exception as e:
            raise GeminiServiceError(f"Gemini extraction failed: {str(e)}")