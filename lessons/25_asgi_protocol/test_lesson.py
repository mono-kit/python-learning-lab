import json

import pytest

from lessons._loader import load_exercise, load_file

call_http_app = load_file("lessons/25_asgi_protocol/example.py")["call_http_app"]

exercise = load_exercise("25_asgi_protocol")
JSONEchoApp = exercise["JSONEchoApp"]
LifespanMiddleware = exercise["LifespanMiddleware"]
ResponseHeaderMiddleware = exercise["ResponseHeaderMiddleware"]


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


async def test_response_middleware_wraps_send_without_changing_the_app() -> None:
    app = ResponseHeaderMiddleware(JSONEchoApp(), b"X-Course", b"asgi")

    response = await call_http_app(app, path="/health")

    assert response.status == 200
    assert response.json() == {"status": "ok"}
    assert response.header("x-course") == "asgi"


async def test_lifespan_middleware_handles_startup_and_shutdown_in_order() -> None:
    async def inner_app(
        _scope: dict[str, object],
        _receive: object,
        _send: object,
    ) -> None:
        raise AssertionError("lifespan 不应交给内层 HTTP app")

    app = LifespanMiddleware(inner_app)
    incoming = iter(
        [
            {"type": "lifespan.startup"},
            {"type": "lifespan.shutdown"},
        ]
    )
    outgoing: list[dict[str, object]] = []
    states: list[bool] = []

    async def receive() -> dict[str, object]:
        return next(incoming)

    async def send(message: dict[str, object]) -> None:
        outgoing.append(message)
        states.append(app.started)

    await app({"type": "lifespan"}, receive, send)

    assert outgoing == [
        {"type": "lifespan.startup.complete"},
        {"type": "lifespan.shutdown.complete"},
    ]
    assert states == [True, False]
    assert not app.started
