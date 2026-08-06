import json

from python_learning_lab.web.asgi_protocol import (
    JSONEchoApp,
    ResponseHeaderMiddleware,
    call_http_app,
)
from python_learning_lab.web.http_stdlib import request_json, running_server


def test_standard_library_http_round_trip() -> None:
    with running_server() as base_url:
        health = request_json(f"{base_url}/health")
        item = request_json(f"{base_url}/items?id=python%20book")
        echo = request_json(
            f"{base_url}/echo",
            method="POST",
            payload={"chapter": 21},
        )
        missing = request_json(f"{base_url}/missing")
        wrong_method = request_json(f"{base_url}/health", method="POST", payload={})
        wrong_method_on_missing = request_json(f"{base_url}/missing", method="PUT")

    assert health.json() == {"status": "ok"}
    assert item.json() == {"id": "python book"}
    assert echo.json() == {"echo": {"chapter": 21}}
    assert missing.status == 404
    assert wrong_method.status == 405
    assert wrong_method.headers["Allow"] == "GET"
    assert wrong_method_on_missing.status == 404


async def test_raw_asgi_app_handles_chunked_body_and_middleware() -> None:
    app = ResponseHeaderMiddleware(JSONEchoApp(), b"x-request-id", b"course-25")
    body = json.dumps({"message": "hello"}).encode()
    response = await call_http_app(
        app,
        method="POST",
        path="/echo",
        body_chunks=(body[:3], body[3:]),
    )

    assert response.status == 200
    assert response.json() == {"echo": {"message": "hello"}}
    assert response.header("x-request-id") == "course-25"


async def test_raw_asgi_app_reports_http_boundaries() -> None:
    app = JSONEchoApp(max_body_bytes=2)

    assert (await call_http_app(app, path="/health")).status == 200
    assert (await call_http_app(app, path="/missing")).status == 404
    assert (await call_http_app(app, method="POST", path="/health")).status == 405
    response = await call_http_app(
        app,
        method="POST",
        path="/echo",
        body_chunks=(b"123",),
    )
    assert response.status == 413
