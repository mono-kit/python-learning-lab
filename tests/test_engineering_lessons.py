import logging
from datetime import UTC, datetime

import pytest

from python_learning_lab.engineering.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from python_learning_lab.engineering.domain import InvalidTransition, TaskStatus
from python_learning_lab.engineering.service import TaskService
from python_learning_lab.engineering.storage import SQLiteTaskRepository
from python_learning_lab.engineering.testing_lab import AuditService, FrozenClock
from python_learning_lab.task_queue.models import CreateTaskInput, TaskOutput


def exercise_service(repository) -> None:
    service = TaskService(repository, SequentialIdGenerator())
    task = service.add("  生成日报  ")

    assert task.title == "生成日报"
    assert service.list() == (task,)

    running = service.start(task.id)
    succeeded = service.succeed(task.id)
    assert running.status is TaskStatus.RUNNING
    assert succeeded.status is TaskStatus.SUCCEEDED

    with pytest.raises(InvalidTransition):
        service.cancel(task.id)


def test_service_works_with_memory_repository(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    exercise_service(MemoryTaskRepository())
    assert "task_added" in caplog.messages


def test_service_works_with_sqlite_repository() -> None:
    repository = SQLiteTaskRepository.connect()
    try:
        repository.initialize()
        exercise_service(repository)
    finally:
        repository.close()


def test_sqlite_transaction_rolls_back_all_writes() -> None:
    repository = SQLiteTaskRepository.connect()
    try:
        repository.initialize()
        with pytest.raises(RuntimeError), repository.transaction() as connection:
            connection.execute(
                "INSERT INTO tasks (id, title, status, error) VALUES (?, ?, ?, ?)",
                ("task-1", "temporary", "pending", None),
            )
            raise RuntimeError("force rollback")
        assert repository.get("task-1") is None
    finally:
        repository.close()


def test_injected_clock_makes_time_test_deterministic() -> None:
    now = datetime(2026, 8, 3, 8, 30, tzinfo=UTC)
    record = AuditService(FrozenClock(now)).record(" deploy ")
    assert record.action == "deploy"
    assert record.occurred_at == now


def test_pydantic_models_stay_at_application_boundary() -> None:
    incoming = CreateTaskInput.model_validate({"title": "  build wheel  "})
    repository = MemoryTaskRepository()
    task = TaskService(repository, SequentialIdGenerator()).add(incoming.title)
    outgoing = TaskOutput.from_domain(task)

    assert outgoing.model_dump() == {
        "id": "task-1",
        "title": "build wheel",
        "status": "pending",
        "error": None,
    }
