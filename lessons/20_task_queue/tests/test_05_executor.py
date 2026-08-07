"""里程碑 5：有界并发执行器；缺失接口时给出下一步提示。"""

import asyncio
from collections.abc import Sequence
from importlib import import_module
from typing import Any

import pytest

from lessons._shared.task_queue.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from lessons._shared.task_queue.domain import Task, TaskStatus
from lessons._shared.task_queue.service import TaskService


def require_task_executor() -> type[Any]:
    module_name = "lessons._shared.task_queue.executor"
    try:
        module = import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name != module_name:
            raise
        module = None

    if module is None:
        pytest.fail(
            "里程碑 5 尚未实现：请新增 task_queue/executor.py，并公开 "
            "TaskExecutor(service, handler, *, workers, timeout)；实例必须提供 "
            "async run_pending() -> Sequence[Task]。详见 lessons/20_task_queue/tests/README.md。",
            pytrace=False,
        )

    executor_type = getattr(module, "TaskExecutor", None)
    if not isinstance(executor_type, type):
        pytest.fail(
            "task_queue.executor 已存在，但没有公开 TaskExecutor 类。最小构造接口为 "
            "TaskExecutor(service, handler, *, workers, timeout)。",
            pytrace=False,
        )
    return executor_type


async def test_executor_isolates_failure_limits_concurrency_and_keeps_order() -> None:
    executor_type = require_task_executor()
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    completed = service.add("already completed")
    service.succeed(service.start(completed.id).id)
    for title in ["first", "fail", "third"]:
        service.add(title)

    active = 0
    maximum = 0
    first_pair_started = asyncio.Event()

    async def handler(task: Task) -> None:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        if maximum == 2:
            first_pair_started.set()
        try:
            await asyncio.wait_for(first_pair_started.wait(), timeout=0.2)
            if task.title == "fail":
                raise RuntimeError("broken")
        finally:
            active -= 1

    executor = executor_type(service, handler, workers=2, timeout=0.1)
    results: Sequence[Task] = await executor.run_pending()

    assert [task.title for task in results] == ["first", "fail", "third"]
    assert [task.status for task in results] == [
        TaskStatus.SUCCEEDED,
        TaskStatus.FAILED,
        TaskStatus.SUCCEEDED,
    ]
    assert results[1].error
    assert maximum == 2


async def test_executor_converts_timeout_to_failed_task() -> None:
    executor_type = require_task_executor()
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    service.add("slow")

    async def slow_handler(_task: Task) -> None:
        await asyncio.sleep(0.05)

    executor = executor_type(service, slow_handler, workers=1, timeout=0.001)
    results: Sequence[Task] = await executor.run_pending()

    assert len(results) == 1
    assert results[0].status is TaskStatus.FAILED
    assert results[0].error
