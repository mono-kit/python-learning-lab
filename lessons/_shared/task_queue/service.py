"""应用服务只编排用例，不知道任务保存在哪里。"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence

from .domain import Task
from .ports import IdGenerator, TaskRepository


class TaskNotFound(LookupError):
    pass


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        generate_id: IdGenerator,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self.repository = repository
        self.generate_id = generate_id
        self.logger = logger or logging.getLogger(__name__)

    def add(self, title: str) -> Task:
        task = Task(id=self.generate_id(), title=title.strip())
        self.repository.save(task)
        self.logger.info("task_added", extra={"task_id": task.id})
        return task

    def list(self) -> Sequence[Task]:
        return self.repository.list()

    def get(self, task_id: str) -> Task:
        """查询单个任务；入口适配器不应直接绕过服务访问仓库。"""

        return self._get(task_id)

    def start(self, task_id: str) -> Task:
        return self._update(task_id, lambda task: task.start())

    def succeed(self, task_id: str) -> Task:
        return self._update(task_id, lambda task: task.succeed())

    def fail(self, task_id: str, reason: str) -> Task:
        task = self._get(task_id).fail(reason)
        self.repository.save(task)
        self.logger.warning("task_failed", extra={"task_id": task.id, "reason": reason})
        return task

    def retry(self, task_id: str) -> Task:
        return self._update(task_id, lambda task: task.retry())

    def cancel(self, task_id: str) -> Task:
        return self._update(task_id, lambda task: task.cancel())

    def _get(self, task_id: str) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def _update(self, task_id: str, operation: Callable[[Task], Task]) -> Task:
        task = self._get(task_id)
        updated = operation(task)
        self.repository.save(updated)
        self.logger.info(
            "task_status_changed",
            extra={"task_id": updated.id, "status": updated.status.value},
        )
        return updated
