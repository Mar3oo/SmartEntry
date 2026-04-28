import sqlite3
import json
from typing import Optional, Dict, Any


class SQLiteStore:
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        # 🔥 NEW STRUCTURE (full pipeline state)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # =========================
    # INSERT / UPDATE
    # =========================
    def save_document(self, file_id: str, data: Dict[str, Any]):
        cursor = self.conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO documents (id, data)
        VALUES (?, ?)
        """,
            (file_id, json.dumps(data)),
        )

        self.conn.commit()

    # =========================
    # READ
    # =========================
    def get_document(self, file_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT data FROM documents WHERE id=?
        """,
            (file_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return json.loads(row[0])
