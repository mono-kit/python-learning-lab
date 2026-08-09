"""第 26 章：用 FastAPI 把既有应用服务暴露为 ASGI HTTP API。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from lessons._loader import load_file
from lessons._shared.task_queue.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from lessons._shared.task_queue.domain import InvalidTransition
from lessons._shared.task_queue.service import TaskNotFound, TaskService

router_module = load_file("lessons/26_asgi_service/router.py")
router = router_module["router"]
require_api_key = router_module["require_api_key"]


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """记录服务器启动与关闭，示范应用级资源生命周期。"""

    application.state.lifecycle_events.append("startup")
    try:
        yield
    finally:
        application.state.lifecycle_events.append("shutdown")


def create_app(service: TaskService | None = None) -> FastAPI:
    """在 composition root 组装依赖，并把业务服务接到 HTTP 边界。"""

    task_service = (
        service
        if service is not None
        else TaskService(
            repository=MemoryTaskRepository(),
            generate_id=SequentialIdGenerator(),
        )
    )
    application = FastAPI(
        title="Task Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    @application.exception_handler(TaskNotFound)
    def task_not_found(_request: Request, error: TaskNotFound) -> JSONResponse:
        return JSONResponse(
            content={"detail": f"task {error.args[0]} not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @application.exception_handler(InvalidTransition)
    def invalid_transition(_request: Request, error: InvalidTransition) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(error)},
            status_code=status.HTTP_409_CONFLICT,
        )

    @application.middleware("http")
    async def add_application_header(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Application"] = "task-service"
        return response

    application.include_router(router)
    application.state.task_service = task_service
    application.state.lifecycle_events = []
    return application


app = create_app()
