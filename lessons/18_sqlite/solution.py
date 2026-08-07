"""第 18 章 SQLiteNoteRepository 参考答案。"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Note:
    id: str
    text: str


class SQLiteNoteRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        with self.connection:
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, text TEXT NOT NULL)"
            )

    def save(self, note: Note) -> None:
        if self.connection.in_transaction:
            self._save(note)
            return
        with self.connection:
            self._save(note)

    def get(self, note_id: str) -> Note | None:
        row = self.connection.execute(
            "SELECT id, text FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        return Note(str(row["id"]), str(row["text"])) if row else None

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        if self.connection.in_transaction:
            raise RuntimeError("不支持嵌套事务")
        self.connection.execute("BEGIN")
        try:
            yield self.connection
        except BaseException:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def _save(self, note: Note) -> None:
        self.connection.execute(
            "INSERT INTO notes (id, text) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET text = excluded.text",
            (note.id, note.text),
        )
