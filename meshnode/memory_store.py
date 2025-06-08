# meshnode/memory_store.py
import sqlite3

class MemoryStore:
    def __init__(self, db_path="mesh_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT
                )
            """)

    def add_memory(self, memory):
        with self.conn:
            self.conn.execute("INSERT INTO memories (content) VALUES (?)", (memory,))

    def get_recent_memories(self, limit=5):
        cur = self.conn.cursor()
        cur.execute("SELECT content FROM memories ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        return [row[0] for row in rows]
