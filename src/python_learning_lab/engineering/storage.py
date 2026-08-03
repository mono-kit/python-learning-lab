"""第 18 章：SQLite、参数绑定、事务和领域对象映射。"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

from .domain import Task, TaskStatus


class SQLiteTaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    @classmethod
    def connect(cls, path: Path | str = ":memory:") -> SQLiteTaskRepository:
        return cls(sqlite3.connect(path))

    def initialize(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error TEXT
                )
                """
            )

    def get(self, task_id: str) -> Task | None:
        row = self.connection.execute(
            "SELECT id, title, status, error FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return self._to_task(row) if row is not None else None

    def list(self) -> Sequence[Task]:
        rows = self.connection.execute(
            "SELECT id, title, status, error FROM tasks ORDER BY rowid"
        ).fetchall()
        return tuple(self._to_task(row) for row in rows)

    def save(self, task: Task) -> None:
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO tasks (id, title, status, error)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    status = excluded.status,
                    error = excluded.error
                """,
                (task.id, task.title, task.status.value, task.error),
            )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """异常离开 with 时回滚，正常离开时提交。"""

        with self.connection:
            yield self.connection

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=str(row["id"]),
            title=str(row["title"]),
            status=TaskStatus(str(row["status"])),
            error=str(row["error"]) if row["error"] is not None else None,
        )
