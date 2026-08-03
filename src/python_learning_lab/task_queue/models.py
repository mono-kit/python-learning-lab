"""Pydantic 只负责系统边界，不侵入领域模型。"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from python_learning_lab.engineering.domain import Task


class CreateTaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)


class TaskOutput(BaseModel):
    id: str
    title: str
    status: str
    error: str | None = None

    @classmethod
    def from_domain(cls, task: Task) -> TaskOutput:
        return cls(
            id=task.id,
            title=task.title,
            status=task.status.value,
            error=task.error,
        )
