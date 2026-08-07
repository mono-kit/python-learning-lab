import pytest

from lessons._loader import load_exercise

exercise = load_exercise("17_architecture")
Task = exercise["Task"]
TaskStatus = exercise["TaskStatus"]
InvalidTransition = exercise["InvalidTransition"]


def test_task_state_is_immutable_and_transitions_are_explicit() -> None:
    pending = Task("task-1", "build wheel")
    running = pending.start()
    failed = running.fail("network unavailable")
    retried = failed.retry()

    assert pending.status is TaskStatus.PENDING
    assert running.status is TaskStatus.RUNNING
    assert failed.status is TaskStatus.FAILED
    assert failed.error == "network unavailable"
    assert retried.status is TaskStatus.PENDING
    assert retried.error is None


def test_task_rejects_illegal_transitions_and_empty_failure_reason() -> None:
    pending = Task("task-1", "build wheel")
    with pytest.raises(InvalidTransition):
        pending.retry()
    with pytest.raises(InvalidTransition):
        pending.fail("too early")
    with pytest.raises(ValueError):
        pending.start().fail("  ")
