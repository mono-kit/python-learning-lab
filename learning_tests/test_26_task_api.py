import httpx

from learning_tests.loader import load_exercise
from python_learning_lab.engineering.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from python_learning_lab.engineering.service import TaskService

exercise = load_exercise("26_task_api.py")
create_app = exercise["create_app"]


async def test_task_service_is_reused_behind_an_http_adapter() -> None:
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    app = create_app(service)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        invalid = await client.post("/tasks", json={"title": "  "})
        created = await client.post("/tasks", json={"title": " learn ASGI "})
        listed = await client.get("/tasks")
        fetched = await client.get("/tasks/task-1")
        started = await client.post("/tasks/task-1/start")
        conflict = await client.post("/tasks/task-1/start")
        missing = await client.get("/tasks/missing")

    assert invalid.status_code == 422
    assert created.status_code == 201
    assert created.json()["title"] == "learn ASGI"
    assert listed.json() == [created.json()]
    assert fetched.json() == created.json()
    assert started.json()["status"] == "running"
    assert conflict.status_code == 409
    assert missing.status_code == 404
