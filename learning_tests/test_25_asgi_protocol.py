import json

import pytest

from learning_tests.loader import load_exercise
from python_learning_lab.web.asgi_protocol import call_http_app

exercise = load_exercise("25_asgi_protocol.py")
JSONEchoApp = exercise["JSONEchoApp"]


async def test_asgi_app_reads_chunked_body_and_sends_response_events() -> None:
    app = JSONEchoApp()
    encoded = json.dumps({"message": "你好"}).encode()
    response = await call_http_app(
        app,
        method="POST",
        path="/echo",
        body_chunks=(encoded[:4], encoded[4:]),
    )

    assert response.status == 200
    assert response.json() == {"echo": {"message": "你好"}}
    assert response.header("content-type") == "application/json; charset=utf-8"
    assert response.header("content-length") == str(len(response.body))


async def test_asgi_app_handles_routes_methods_and_body_limit() -> None:
    app = JSONEchoApp()

    assert (await call_http_app(app, path="/health")).status == 200
    assert (await call_http_app(app, method="POST", path="/health")).status == 405
    assert (await call_http_app(app, path="/missing")).status == 404

    tiny_app = JSONEchoApp(max_body_bytes=2)
    too_large = await call_http_app(
        tiny_app,
        method="POST",
        path="/echo",
        body_chunks=(b"{} ",),
    )
    assert too_large.status == 413


async def test_asgi_app_rejects_unknown_scope() -> None:
    async def receive() -> dict[str, object]:
        return {"type": "websocket.connect"}

    async def send(_message: dict[str, object]) -> None:
        pass

    with pytest.raises(ValueError):
        await JSONEchoApp()({"type": "websocket"}, receive, send)
