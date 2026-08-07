"""第 18 章练习：实现一个最小 SQLite 仓库。"""

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
        # TODO: 在事务中创建 notes(id TEXT PRIMARY KEY, text TEXT NOT NULL)。
        raise NotImplementedError

    def save(self, note: Note) -> None:
        # TODO: 使用参数绑定和 ON CONFLICT 更新。单独调用时提交；如果已经位于
        # transaction() 中，则只能加入外层事务，不能提前提交。
        raise NotImplementedError

    def get(self, note_id: str) -> Note | None:
        # TODO: 使用 WHERE id = ?，找不到返回 None。
        raise NotImplementedError

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        # TODO: 显式开始事务，正常退出提交，任何异常退出都回滚；拒绝嵌套事务。
        raise NotImplementedError
        yield self.connection
