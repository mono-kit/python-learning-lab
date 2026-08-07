"""第 26 章：用 FastAPI 把既有应用服务暴露为 ASGI HTTP API。"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from lessons._shared.task_queue.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from lessons._shared.task_queue.domain import InvalidTransition
from lessons._shared.task_queue.models import CreateTaskInput, TaskOutput
from lessons._shared.task_queue.service import TaskNotFound, TaskService


def create_app(service: TaskService | None = None) -> FastAPI:
    """应用工厂是 composition root；路由只做 HTTP 与应用服务之间的转换。"""

    task_service = service or TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    application = FastAPI(title="Python Learning Task API", version="1.0.0")

    @application.exception_handler(TaskNotFound)
    async def task_not_found(_request: Request, error: TaskNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": f"task {error.args[0]} not found"})

    @application.exception_handler(InvalidTransition)
    async def invalid_transition(_request: Request, error: InvalidTransition) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @application.post("/tasks", response_model=TaskOutput, status_code=status.HTTP_201_CREATED)
    def add_task(payload: CreateTaskInput) -> TaskOutput:
        return TaskOutput.from_domain(task_service.add(payload.title))

    @application.get("/tasks", response_model=list[TaskOutput])
    def list_tasks() -> list[TaskOutput]:
        return [TaskOutput.from_domain(task) for task in task_service.list()]

    @application.get("/tasks/{task_id}", response_model=TaskOutput)
    def get_task(task_id: str) -> TaskOutput:
        return TaskOutput.from_domain(task_service.get(task_id))

    @application.post("/tasks/{task_id}/start", response_model=TaskOutput)
    def start_task(task_id: str) -> TaskOutput:
        return TaskOutput.from_domain(task_service.start(task_id))

    application.state.task_service = task_service
    return application


app = create_app()
