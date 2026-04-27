import pandas as pd
from typing import Dict, Any


class ExcelExporter:
    def export(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Export structured data to Excel.
        """

        rows = []

        invoice = data.get("invoice", {})
        totals = data.get("totals", {})
        items = data.get("items", [])

        if not items:
            rows.append({
                "invoice_number": invoice.get("invoice_number"),
                "invoice_date": invoice.get("invoice_date"),
                "total": totals.get("total"),
                "currency": data.get("currency"),
                "item_description": None,
                "quantity": None,
                "unit_price": None,
                "total_price": None
            })
        else:
            for item in items:
                rows.append({
                    "invoice_number": invoice.get("invoice_number"),
                    "invoice_date": invoice.get("invoice_date"),
                    "total": totals.get("total"),
                    "currency": data.get("currency"),
                    "item_description": item.get("description"),
                    "quantity": item.get("quantity"),
                    "unit_price": item.get("unit_price"),
                    "total_price": item.get("total_price")
                })

        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)

        return output_path