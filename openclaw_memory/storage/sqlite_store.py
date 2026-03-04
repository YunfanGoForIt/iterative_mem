from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteStore:
    def __init__(self, path: str = "neuromem.db") -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self._init_tables()

    def _init_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                content TEXT NOT NULL,
                salience REAL NOT NULL,
                trust REAL NOT NULL,
                confidence REAL NOT NULL
            )
            """
        )
        self.conn.commit()

    def persist_memory(self, memory_id: str, task_id: str, content: str, salience: float, trust: float, confidence: float) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO memories(id, task_id, content, salience, trust, confidence) VALUES (?, ?, ?, ?, ?, ?)",
            (memory_id, task_id, content, salience, trust, confidence),
        )
        self.conn.commit()
