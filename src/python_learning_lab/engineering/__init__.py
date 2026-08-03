"""Python 工程实践课程：边界、架构、测试和持久化。"""

from .domain import Task, TaskStatus
from .service import TaskService

__all__ = ["Task", "TaskService", "TaskStatus"]
