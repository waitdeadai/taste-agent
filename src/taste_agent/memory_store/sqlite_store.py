"""SQLite-backed taste.memory store (optional, for high-volume projects).

Schema:
  taste_memory_entries (
    entry_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    task_hash TEXT NOT NULL,
    task_description TEXT NOT NULL,
    file_path TEXT NOT NULL,
    verdict TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    issues TEXT DEFAULT '[]',
    principle TEXT NOT NULL,
    category TEXT NOT NULL,
    was_applied INTEGER DEFAULT 0,
    applied_correctly INTEGER,
    UNIQUE(task_hash, file_path)
  )
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from taste_agent.core.memory import MemoryEntry, TasteMemory


class SQLiteStore(TasteMemory):
    """SQLite-backed taste.memory store.

    Alternative to JSONL file store for high-volume projects
    that benefit from SQL queries and indexing.
    """

    def __init__(self, path: Path | str = ".taste/taste.db"):
        self.db_path = Path(path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    @contextmanager
    def _conn_context(self) -> Generator[sqlite3.Connection, None, None]:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        try:
            yield self._conn
        finally:
            pass  # Keep connection open

    def _ensure_schema(self) -> None:
        with self._conn_context() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS taste_memory_entries (
                    entry_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    task_hash TEXT NOT NULL,
                    task_description TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    issues TEXT DEFAULT '[]',
                    principle TEXT NOT NULL,
                    category TEXT NOT NULL,
                    was_applied INTEGER DEFAULT 0,
                    applied_correctly INTEGER,
                    UNIQUE(task_hash, file_path)
                );
                CREATE INDEX IF NOT EXISTS idx_category ON taste_memory_entries(category);
                CREATE INDEX IF NOT EXISTS idx_verdict ON taste_memory_entries(verdict);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON taste_memory_entries(timestamp DESC);
            """)

    def _load(self) -> list[MemoryEntry]:
        entries = []
        with self._conn_context() as conn:
            rows = conn.execute(
                "SELECT * FROM taste_memory_entries ORDER BY timestamp ASC"
            ).fetchall()
            for row in rows:
                entries.append(MemoryEntry(
                    entry_id=row["entry_id"],
                    timestamp=row["timestamp"],
                    task_hash=row["task_hash"],
                    task_description=row["task_description"],
                    file_path=row["file_path"],
                    verdict=row["verdict"],
                    reasoning=row["reasoning"],
                    issues=json.loads(row["issues"]),
                    principle=row["principle"],
                    category=row["category"],
                    was_applied=bool(row["was_applied"]),
                    applied_correctly=bool(row["applied_correctly"]) if row["applied_correctly"] is not None else None,
                ))
        return entries

    def add_entry(self, entry: MemoryEntry) -> None:
        with self._conn_context() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO taste_memory_entries
                (entry_id, timestamp, task_hash, task_description, file_path,
                 verdict, reasoning, issues, principle, category, was_applied, applied_correctly)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.entry_id,
                    entry.timestamp,
                    entry.task_hash,
                    entry.task_description,
                    entry.file_path,
                    entry.verdict,
                    entry.reasoning,
                    json.dumps(entry.issues),
                    entry.principle,
                    entry.category,
                    int(entry.was_applied),
                    int(entry.applied_correctly) if entry.applied_correctly is not None else None,
                ),
            )
            conn.commit()

    def entries_by_category(self, category: str) -> list[MemoryEntry]:
        with self._conn_context() as conn:
            rows = conn.execute(
                "SELECT * FROM taste_memory_entries WHERE category = ? ORDER BY timestamp ASC",
                (category,),
            ).fetchall()
            return [self._row_to_entry(r) for r in rows]

    def entries_by_verdict(self, verdict: str) -> list[MemoryEntry]:
        with self._conn_context() as conn:
            rows = conn.execute(
                "SELECT * FROM taste_memory_entries WHERE verdict = ? ORDER BY timestamp ASC",
                (verdict,),
            ).fetchall()
            return [self._row_to_entry(r) for r in rows]

    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            entry_id=row["entry_id"],
            timestamp=row["timestamp"],
            task_hash=row["task_hash"],
            task_description=row["task_description"],
            file_path=row["file_path"],
            verdict=row["verdict"],
            reasoning=row["reasoning"],
            issues=json.loads(row["issues"]),
            principle=row["principle"],
            category=row["category"],
            was_applied=bool(row["was_applied"]),
            applied_correctly=bool(row["applied_correctly"]) if row["applied_correctly"] is not None else None,
        )
