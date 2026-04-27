import json
import time
from typing import Dict, Any, Optional
import os

from groq import Groq


class GroqServiceError(Exception):
    pass


class GroqService:
    def __init__(self, model: str = "llama3-70b-8192"):
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
    "total": number | null
  }},
  "currency": string | null,
  "extra_fields": {{}}
}}

Rules:
- Output ONLY JSON (no explanation)
- Use null for missing fields
- Numbers must be numeric (not strings)

Text:
{text}
"""

    def extract(self, text: str, blocks: Optional[list] = None) -> Dict[str, Any]:
        if self.client is None:
            raise GroqServiceError("Groq client not initialized (missing API key)")
        
        prompt = self._build_prompt(text)

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )

                content = response.choices[0].message.content.strip()

                # Try parsing JSON
                return json.loads(content)

            except Exception as e:
                if attempt == 2:
                    raise GroqServiceError(f"Groq failed after retries: {str(e)}")

                time.sleep(1)