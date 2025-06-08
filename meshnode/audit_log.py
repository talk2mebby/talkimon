import sqlite3
import json

class AuditLog:
    def __init__(self, db_path="audit_log.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def store(self, action):
        with self.conn:
            self.conn.execute(
                "INSERT INTO audit_log (action_json) VALUES (?)",
                (json.dumps(action),)
            )
            print("[AuditLog] Action logged")
