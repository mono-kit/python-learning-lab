import httpx
from fastapi.testclient import TestClient

from lessons._loader import load_exercise
from lessons._shared.task_queue.adapters import (
    MemoryTaskRepository,
    SequentialIdGenerator,
)
from lessons._shared.task_queue.service import TaskService

exercise = load_exercise("26_asgi_service")
create_app = exercise["create_app"]
require_api_key = exercise["require_api_key"]


async def test_task_service_is_reused_behind_an_http_adapter() -> None:
    service = TaskService(MemoryTaskRepository(), SequentialIdGenerator())
    app = create_app(service)

    assert app.state.task_service is service

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        invalid = await client.post(
            "/tasks", json={"title": "  "}, headers={"X-API-Key": "learning-secret"}
        )
        created = await client.post(
            "/tasks", json={"title": " learn ASGI "}, headers={"X-API-Key": "learning-secret"}
        )
        listed = await client.get("/tasks")
        fetched = await client.get("/tasks/task-1")
        started = await client.post("/tasks/task-1/start", headers={"X-API-Key": "learning-secret"})
        conflict = await client.post(
            "/tasks/task-1/start", headers={"X-API-Key": "learning-secret"}
        )
        missing = await client.get("/tasks/missing")

    assert invalid.status_code == 422
    error = invalid.json()["detail"][0]
    assert error["loc"] == ["body", "title"]
    assert error["type"] == "string_too_short"
    assert created.status_code == 201
    assert created.json()["title"] == "learn ASGI"
    assert listed.json() == [created.json()]
    assert fetched.json() == created.json()
    assert started.json()["status"] == "running"
    assert conflict.status_code == 409
    assert missing.status_code == 404
    assert created.headers["X-Application"] == "task-service"
    assert missing.headers["X-Application"] == "task-service"


async def test_default_applications_have_isolated_state() -> None:
    app_a = create_app()
    app_b = create_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app_a),
        base_url="http://testserver",
    ) as client_a:
        await client_a.post(
            "/tasks", json={"title": " learn ASGI "}, headers={"X-API-Key": "learning-secret"}
        )
        tasks_a = await client_a.get("/tasks")
        assert len(tasks_a.json()) == 1

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app_b),
        base_url="http://testserver",
    ) as client_b:
        tasks_b = await client_b.get("/tasks")
        assert len(tasks_b.json()) == 0


async def test_application_factory_can_build_its_default_composition_root() -> None:
    app = create_app()

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_lifespan_calls_startup_and_shutdown() -> None:
    app = create_app()

    assert app.state.lifecycle_events == []

    with TestClient(app) as client:
        assert app.state.lifecycle_events == ["startup"]

        response = client.get("/tasks")

        assert response.status_code == 200
        assert response.json() == []
        assert response.headers["X-Application"] == "task-service"

    assert app.state.lifecycle_events == ["startup", "shutdown"]


async def test_api_key_is_required() -> None:
    app = create_app()

    def bypass_api_key() -> None:
        return None

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/tasks", json={"title": " learn ASGI "})

        assert response.status_code == 401
        assert response.json()["detail"] == "invalid API key"
        assert response.headers["X-Application"] == "task-service"

        response_b = await client.post(
            "/tasks", json={"title": " learn ASGI "}, headers={"X-API-Key": "invalid-secret"}
        )

        assert response_b.status_code == 401
        assert response_b.json()["detail"] == "invalid API key"
        assert response_b.headers["X-Application"] == "task-service"

        response_c = await client.post(
            "/tasks", json={"title": " learn ASGI "}, headers={"X-API-Key": "learning-secret"}
        )

        assert response_c.status_code == 201
        assert response_c.json()["title"] == "learn ASGI"

        try:
            app.dependency_overrides[require_api_key] = bypass_api_key

            response_d = await client.post("/tasks", json={"title": " learn ASGI "})

            assert response_d.status_code == 201
            assert response_d.json()["title"] == "learn ASGI"
            assert response_d.headers["X-Application"] == "task-service"
        finally:
            app.dependency_overrides.clear()
