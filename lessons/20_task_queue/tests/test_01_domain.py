"""里程碑 1：领域状态机不依赖数据库、CLI 或 Pydantic。"""

import pytest

from lessons._shared.task_queue.domain import InvalidTransition, Task, TaskStatus


def test_success_failure_retry_and_cancel_paths_are_explicit() -> None:
    pending = Task("task-1", "build wheel")
    running = pending.start()
    succeeded = running.succeed()

    failed = Task("task-2", "publish").start().fail("network unavailable")
    retried = failed.retry()
    cancelled = Task("task-3", "obsolete").cancel()

    assert pending.status is TaskStatus.PENDING
    assert running.status is TaskStatus.RUNNING
    assert succeeded.status is TaskStatus.SUCCEEDED
    assert failed.status is TaskStatus.FAILED
    assert failed.error == "network unavailable"
    assert retried.status is TaskStatus.PENDING
    assert retried.error is None
    assert cancelled.status is TaskStatus.CANCELLED


def test_task_rejects_invalid_data_and_transitions() -> None:
    with pytest.raises(ValueError):
        Task("", "title")
    with pytest.raises(ValueError):
        Task("task-1", " ")
    with pytest.raises(ValueError):
        Task("task-1", "title", TaskStatus.FAILED)
    with pytest.raises(ValueError):
        Task("task-1", "title", error="not allowed")

    pending = Task("task-1", "title")
    with pytest.raises(InvalidTransition):
        pending.succeed()
    with pytest.raises(InvalidTransition):
        pending.retry()
    with pytest.raises(InvalidTransition):
        pending.fail("too early")
    with pytest.raises(ValueError):
        pending.start().fail(" ")
