import sqlite3
from typing import List


class AuditLog:
    def __init__(self, db_path: str = "data/app.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            status TEXT,
            errors TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def log(self, file_id: str, status: str, errors: List[str]):
        cursor = self.conn.cursor()

        cursor.execute(
            """
        INSERT INTO audit_log (file_id, status, errors)
        VALUES (?, ?, ?)
        """,
            (file_id, status, ", ".join(errors)),
        )

        self.conn.commit()

    def get_logs(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT file_id, status, errors FROM audit_log")

        return cursor.fetchall()
