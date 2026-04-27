import sqlite3
import json
from typing import Dict, Any, Optional


class SchemaMemory:
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schemas (
            company_id TEXT PRIMARY KEY,
            schema TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    # =========================
    # Save schema
    # =========================

    def save_schema(self, company_id: str, schema: Dict[str, Any]):
        cursor = self.conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO schemas (company_id, schema)
        VALUES (?, ?)
        """,
            (company_id, json.dumps(schema)),
        )

        self.conn.commit()

    # =========================
    # Get schema
    # =========================
    def get_schema(self, company_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()

        cursor.execute(
            """
        SELECT schema FROM schemas WHERE company_id=?
        """,
            (company_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        return json.loads(row[0])
