import pytest

httpx = pytest.importorskip("httpx")
pytest.importorskip("fastapi")

from python_learning_lab.engineering.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from python_learning_lab.engineering.service import TaskService
from python_learning_lab.web.service_api import create_app


async def test_fastapi_is_only_an_adapter_around_task_service() -> None:
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    app = create_app(service)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        created = await client.post("/tasks", json={"title": " learn HTTP "})
        fetched = await client.get("/tasks/task-1")
        started = await client.post("/tasks/task-1/start")
        conflict = await client.post("/tasks/task-1/start")
        missing = await client.get("/tasks/missing")

    assert created.status_code == 201
    assert created.json()["title"] == "learn HTTP"
    assert fetched.json() == created.json()
    assert started.json()["status"] == "running"
    assert conflict.status_code == 409
    assert missing.status_code == 404
