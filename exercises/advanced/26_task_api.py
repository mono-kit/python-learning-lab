"""第 26 章练习：把 TaskService 接到 FastAPI HTTP 边界。"""

from __future__ import annotations

from fastapi import FastAPI

from python_learning_lab.engineering.service import TaskService


def create_app(service: TaskService) -> FastAPI:
    """实现 POST/GET /tasks、GET /tasks/{id} 和 POST /tasks/{id}/start。"""

    # TODO: 路由只转换边界对象并调用 service；映射 404 与 409 领域错误。
    raise NotImplementedError
