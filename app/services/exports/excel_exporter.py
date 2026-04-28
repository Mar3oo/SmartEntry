import pandas as pd
from typing import List, Dict


class ExcelExporter:
    def export(self, rows: List[Dict], output_path: str) -> str:
        """
        Export mapped rows directly to Excel.
        """

        if not rows:
            raise ValueError("No data to export")

        df = pd.DataFrame(rows)
        df.to_excel(output_path, index=False)

        return output_path
