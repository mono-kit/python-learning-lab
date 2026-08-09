"""第 26 章的任务路由、服务依赖与写操作认证。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from lessons._shared.task_queue.models import (
    CreateTaskInput,
    TaskOutput,
)
from lessons._shared.task_queue.service import TaskService


def get_task_service(request: Request) -> TaskService:
    return request.app.state.task_service


TaskServiceDependency = Annotated[TaskService, Depends(get_task_service)]

APIKeyHeader = Annotated[str | None, Header(alias="X-API-Key")]


def require_api_key(api_key: APIKeyHeader = None) -> None:
    if api_key != "learning-secret":
        raise HTTPException(status_code=401, detail="invalid API key")


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post(
    "",
    response_model=TaskOutput,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def add_task(service: TaskServiceDependency, payload: CreateTaskInput) -> TaskOutput:
    return TaskOutput.from_domain(service.add(payload.title))


@router.get(
    "",
    response_model=list[TaskOutput],
)
def list_tasks(service: TaskServiceDependency) -> list[TaskOutput]:
    return [TaskOutput.from_domain(task) for task in service.list()]


@router.post(
    "/{task_id}/start",
    response_model=TaskOutput,
    dependencies=[Depends(require_api_key)],
)
def start_task(service: TaskServiceDependency, task_id: str) -> TaskOutput:
    return TaskOutput.from_domain(service.start(task_id))


@router.get(
    "/{task_id}",
    response_model=TaskOutput,
)
def get_task(service: TaskServiceDependency, task_id: str) -> TaskOutput:
    return TaskOutput.from_domain(service.get(task_id))
