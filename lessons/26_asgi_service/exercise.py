"""第 26 章练习：把 TaskService 接到 FastAPI HTTP 边界。"""

from __future__ import annotations

from fastapi import FastAPI

from lessons._shared.task_queue.service import TaskService


def create_app(service: TaskService | None = None) -> FastAPI:
    """实现 POST/GET /tasks、GET /tasks/{id} 和 POST /tasks/{id}/start。"""

    # TODO: service 为 None 时在 composition root 组装默认内存实现。
    # 路由只转换边界对象并调用 service；映射 404 与 409 领域错误。
    raise NotImplementedError
