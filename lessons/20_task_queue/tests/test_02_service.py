"""里程碑 2：服务依赖结构化端口，并可替换具体适配器。"""

import logging

import pytest

from lessons._shared.task_queue.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from lessons._shared.task_queue.domain import InvalidTransition, TaskStatus
from lessons._shared.task_queue.service import TaskNotFound, TaskService


def test_service_runs_use_cases_with_memory_adapters(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator(prefix="job"))

    first = service.add("  build wheel  ")
    second = service.add("publish")
    assert (first.id, first.title) == ("job-1", "build wheel")
    assert second.id == "job-2"
    assert service.list() == (first, second)

    assert service.start(first.id).status is TaskStatus.RUNNING
    assert service.succeed(first.id).status is TaskStatus.SUCCEEDED

    failed = service.fail(service.start(second.id).id, "network unavailable")
    assert failed.status is TaskStatus.FAILED
    assert service.retry(second.id).status is TaskStatus.PENDING
    assert "task_added" in caplog.messages
    assert "task_failed" in caplog.messages


def test_service_exposes_domain_and_not_found_errors() -> None:
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    task = service.add("pending")

    with pytest.raises(InvalidTransition):
        service.succeed(task.id)
    with pytest.raises(TaskNotFound):
        service.get("missing")
