"""第 17 章练习：实现与框架、日志和数据库无关的状态机。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"


class InvalidTransition(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    error: str | None = None

    def start(self) -> Task:
        # TODO: 只允许 PENDING → RUNNING，并返回新对象。
        raise NotImplementedError

    def fail(self, reason: str) -> Task:
        # TODO: 只允许 RUNNING → FAILED；原因不能为空。
        raise NotImplementedError

    def retry(self) -> Task:
        # TODO: 只允许 FAILED → PENDING，并清除 error。
        raise NotImplementedError
