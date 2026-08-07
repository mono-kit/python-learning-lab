"""第 17 章：不依赖 CLI、数据库或 Pydantic 的领域模型。"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidTransition(ValueError):
    """任务状态变化不符合领域规则。"""


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    error: str | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("任务 id 不能为空")
        if not self.title.strip():
            raise ValueError("任务标题不能为空")
        if self.status is TaskStatus.FAILED and not self.error:
            raise ValueError("失败任务必须记录错误原因")
        if self.status is not TaskStatus.FAILED and self.error is not None:
            raise ValueError("只有失败任务可以记录错误原因")

    def start(self) -> Task:
        self._require(TaskStatus.PENDING)
        return replace(self, status=TaskStatus.RUNNING)

    def succeed(self) -> Task:
        self._require(TaskStatus.RUNNING)
        return replace(self, status=TaskStatus.SUCCEEDED)

    def fail(self, reason: str) -> Task:
        self._require(TaskStatus.RUNNING)
        if not reason.strip():
            raise ValueError("失败原因不能为空")
        return replace(self, status=TaskStatus.FAILED, error=reason)

    def retry(self) -> Task:
        self._require(TaskStatus.FAILED)
        return replace(self, status=TaskStatus.PENDING, error=None)

    def cancel(self) -> Task:
        self._require(TaskStatus.PENDING)
        return replace(self, status=TaskStatus.CANCELLED)

    def _require(self, expected: TaskStatus) -> None:
        if self.status is not expected:
            raise InvalidTransition(
                f"{self.status.value} 状态不能执行该操作；需要 {expected.value}"
            )
