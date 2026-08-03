"""应用核心依赖的 Protocol；实现可以来自内存、SQLite 或其他适配器。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .domain import Task


class TaskRepository(Protocol):
    def get(self, task_id: str) -> Task | None: ...

    def list(self) -> Sequence[Task]: ...

    def save(self, task: Task) -> None: ...


class IdGenerator(Protocol):
    def __call__(self) -> str: ...
