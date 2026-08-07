"""里程碑 3：SQLite 负责持久化、参数绑定和事务原子性。"""

from pathlib import Path

import pytest

from lessons._shared.task_queue.domain import Task
from lessons._shared.task_queue.storage import SQLiteTaskRepository


def test_sqlite_round_trip_update_and_parameter_binding(tmp_path: Path) -> None:
    path = tmp_path / "tasks.sqlite3"
    repository = SQLiteTaskRepository.connect(path)
    try:
        repository.initialize()
        suspicious_title = "Robert'); DROP TABLE tasks;--"
        task = Task("task-1", suspicious_title)
        repository.save(task)
        assert repository.get(task.id) == task

        succeeded = task.start().succeed()
        repository.save(succeeded)
        assert repository.get(task.id) == succeeded
        assert repository.get("missing") is None
    finally:
        repository.close()

    reopened = SQLiteTaskRepository.connect(path)
    try:
        assert reopened.get("task-1") == succeeded
    finally:
        reopened.close()


def test_sqlite_transaction_rolls_back_all_repository_writes() -> None:
    repository = SQLiteTaskRepository.connect()
    try:
        repository.initialize()
        with pytest.raises(RuntimeError), repository.transaction():
            repository.save(Task("task-1", "first"))
            repository.save(Task("task-2", "second"))
            raise RuntimeError("force rollback")

        assert repository.get("task-1") is None
        assert repository.get("task-2") is None
    finally:
        repository.close()
