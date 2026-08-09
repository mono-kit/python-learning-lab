"""第 26 章练习：把 TaskService 接到 FastAPI HTTP 边界。"""

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
from lessons._shared.task_queue.service import (
    TaskNotFound,
    TaskService,
)

router_module = load_file("lessons/26_asgi_service/router.py")
router = router_module["router"]
require_api_key = router_module["require_api_key"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.lifecycle_events.append("startup")
    try:
        yield
    finally:
        app.state.lifecycle_events.append("shutdown")


def create_app(service: TaskService | None = None) -> FastAPI:
    """实现 POST/GET /tasks、GET /tasks/{id} 和 POST /tasks/{id}/start。"""

    task_service = (
        service
        if service is not None
        else TaskService(
            repository=MemoryTaskRepository(),
            generate_id=SequentialIdGenerator(),
        )
    )

    app = FastAPI(
        title="Task Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.exception_handler(TaskNotFound)
    def task_not_found(_request: Request, exc: TaskNotFound) -> JSONResponse:
        return JSONResponse(
            content={"detail": f"task {exc.args[0]} not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(InvalidTransition)
    def invalid_transition(_request: Request, exc: InvalidTransition) -> JSONResponse:
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.middleware("http")
    async def add_application_header(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Application"] = "task-service"
        return response

    app.include_router(router)

    app.state.task_service = task_service
    app.state.lifecycle_events = []

    return app


app = create_app()
