import os
import json
import re
from typing import Dict, Any

from google import genai
from dotenv import load_dotenv
from google.genai import types

load_dotenv()


class GeminiServiceError(Exception):
    pass


class GeminiService:
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise GeminiServiceError("Missing GOOGLE_API_KEY")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _build_prompt(self) -> str:
        return """
You are an invoice extraction system.

Extract structured invoice data from the image.

Return ONLY valid JSON with this schema:

{
  "supplier": null,
  "customer": null,
  "invoice": {
    "invoice_number": string | null,
    "invoice_date": string | null
  },
  "items": [
    {
      "description": string | null,
      "quantity": number | null,
      "unit_price": number | null,
      "total_price": number | null
    }
  ],
  "totals": {
    "net_total": number | null,
    "vat": number | null,
    "gross_total": number | null
  },
  "currency": string | null,
  "extra_fields": {}
}

STRICT RULES:
- JSON ONLY
- No explanation
- Numbers must be numeric
- Use null for missing fields
- currency should be ISO code (e.g. "USD", "EUR")
- net_total = sum of item net totals
- vat = total VAT amount if available
- gross_total = net_total + vat
"""

    def _safe_json(self, text: str):
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Invalid JSON: {text}")

    def _normalize(self, data: dict):
        for field in ["supplier", "customer"]:
            val = data.get(field)
            if isinstance(val, str):
                data[field] = {"name": val, "address": None, "tax_id": None}
            elif val is None:
                data[field] = {"name": None, "address": None, "tax_id": None}
        return data

    def extract(self, data: dict) -> Dict[str, Any]:
        file_path = data.get("file_path")

        if not file_path:
            raise GeminiServiceError("file_path is required")

        try:
            prompt = self._build_prompt()

            with open(file_path, "rb") as f:
                image_bytes = f.read()

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(
                                data=image_bytes, mime_type="image/jpeg"
                            ),
                        ]
                    )
                ],
            )

            content = response.text

            print("\n========== GEMINI RAW RESPONSE ==========")
            print(content)
            print("========================================\n")

            parsed = self._safe_json(content)

            return self._normalize(parsed)

        except Exception as e:
            raise GeminiServiceError(f"Gemini extraction failed: {str(e)}")
