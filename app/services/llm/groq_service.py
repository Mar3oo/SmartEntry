import json
import time
import re
from typing import Dict, Any
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqServiceError(Exception):
    pass


class GroqService:
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

        self.model = model

    def _build_prompt(self, text: str) -> str:
        return f"""
You are an information extraction system.

Extract structured invoice data from the text below.

Return ONLY valid JSON with this exact schema:

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
    "net_total": number | null,
    "vat": number | null,
    "gross_total": number | null
  }},
  "currency": string | null,
  "extra_fields": {{}}
}}

Rules:
- Return ONLY valid JSON
- No explanation
- No markdown
- No text before or after JSON
- If output is not valid JSON, the system will fail
- Use null for missing fields
- Numbers must be numeric (not strings)
- currency should be ISO code (e.g. "USD", "EUR")
- net_total = sum of item net totals
- vat = total VAT amount if available
- gross_total = net_total + vat

Text:
{text}
"""

    def _safe_json_load(self, text: str):
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Invalid JSON from LLM: {text}")

    def extract(self, data: dict) -> Dict[str, Any]:
        text = data.get("text", "")

        if self.client is None:
            raise GroqServiceError("Groq client not initialized (missing API key)")

        prompt = self._build_prompt(text)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )

                content = response.choices[0].message.content.strip()

                # # 🔥 Debug output
                # print("\n========== GROQ RAW RESPONSE ==========")
                # print(content)
                # print("======================================\n")

                parsed = self._safe_json_load(content)
                return self._normalize_output(parsed)

            except Exception as e:
                if attempt == 2:
                    raise GroqServiceError(f"Groq failed after retries: {str(e)}")

                time.sleep(1)

    def _normalize_output(self, data: dict) -> dict:
        # Fix supplier/customer if they come as string
        for field in ["supplier", "customer"]:
            value = data.get(field)

            if isinstance(value, str):
                data[field] = {"name": value, "address": None, "tax_id": None}

            elif value is None:
                data[field] = {"name": None, "address": None, "tax_id": None}

        return data
