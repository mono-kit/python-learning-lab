"""第 17 章适配器：内存仓库、ID 生成器和日志配置。"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from itertools import count

from .domain import Task


class MemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list(self) -> Sequence[Task]:
        return tuple(self._tasks.values())

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task


class SequentialIdGenerator:
    def __init__(self, prefix: str = "task") -> None:
        self.prefix = prefix
        self._numbers = count(1)

    def __call__(self) -> str:
        return f"{self.prefix}-{next(self._numbers)}"


def configure_logging(level: int = logging.INFO) -> None:
    """入口层配置 handler；库代码只获取 logger 并记录事件。"""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
