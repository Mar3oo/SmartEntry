import sqlite3
import json
from typing import Optional, Dict, Any


class SQLiteStore:
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            raw_text TEXT,
            structured_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # =========================
    # INSERT
    # =========================
    def save_document(
        self, file_id: str, raw_text: str, structured_data: Dict[str, Any]
    ):
        cursor = self.conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO documents (id, raw_text, structured_data)
        VALUES (?, ?, ?)
        """,
            (file_id, raw_text, json.dumps(structured_data)),
        )

        self.conn.commit()

    # =========================
    # READ
    # =========================
    def get_document(self, file_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT raw_text, structured_data FROM documents WHERE id=?
        """,
            (file_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return {"raw_text": row[0], "structured_data": json.loads(row[1])}
