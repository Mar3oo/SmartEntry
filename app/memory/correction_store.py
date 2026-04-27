import sqlite3
import json
from typing import Dict, Any, Optional


class CorrectionStore:
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            file_id TEXT PRIMARY KEY,
            original_data TEXT,
            corrected_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # =========================
    # Save correction
    # =========================
    def save_correction(
        self,
        file_id: str,
        original_data: Dict[str, Any],
        corrected_data: Dict[str, Any],
    ):
        cursor = self.conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO corrections (file_id, original_data, corrected_data)
        VALUES (?, ?, ?)
        """,
            (file_id, json.dumps(original_data), json.dumps(corrected_data)),
        )

        self.conn.commit()

    # =========================
    # Get correction
    # =========================
    def get_correction(self, file_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT original_data, corrected_data FROM corrections WHERE file_id=?
        """,
            (file_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "original_data": json.loads(row[0]),
            "corrected_data": json.loads(row[1]),
        }
