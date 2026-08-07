"""第 25 章：不依赖 Web 框架实现并测试 ASGI 应用。"""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class ASGIApplication(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


class ClientDisconnected(ConnectionError):
    pass


class RequestBodyTooLarge(ValueError):
    pass


async def read_http_body(receive: Receive, *, max_bytes: int = 1_000_000) -> bytes:
    """持续消费 ``http.request``，直到 ``more_body`` 为假。"""

    if max_bytes < 0:
        raise ValueError("max_bytes 不能为负数")
    chunks: list[bytes] = []
    size = 0
    while True:
        message = await receive()
        message_type = message.get("type")
        if message_type == "http.disconnect":
            raise ClientDisconnected
        if message_type != "http.request":
            raise RuntimeError(f"unexpected ASGI message: {message_type!r}")
        chunk = message.get("body", b"")
        if not isinstance(chunk, bytes):
            raise TypeError("http.request body 必须是 bytes")
        size += len(chunk)
        if size > max_bytes:
            raise RequestBodyTooLarge
        chunks.append(chunk)
        if not message.get("more_body", False):
            return b"".join(chunks)


async def send_json(
    send: Send,
    status: int,
    payload: object,
    *,
    headers: Sequence[tuple[bytes, bytes]] = (),
) -> None:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                (b"content-length", str(len(body)).encode("ascii")),
                *headers,
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


class JSONEchoApp:
    """支持 ``GET /health`` 与 ``POST /echo`` 的原生 ASGI 应用。"""

    def __init__(self, *, max_body_bytes: int = 1_000_000) -> None:
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            raise ValueError(f"unsupported scope type: {scope.get('type')!r}")

        method = scope.get("method")
        path = scope.get("path")
        if path == "/health" and method == "GET":
            await send_json(send, 200, {"status": "ok"})
            return
        if path == "/echo" and method == "POST":
            try:
                body = await read_http_body(receive, max_bytes=self.max_body_bytes)
            except RequestBodyTooLarge:
                await send_json(send, 413, {"error": "body too large"})
                return
            except ClientDisconnected:
                return
            try:
                payload = json.loads(body)
            except (UnicodeDecodeError, json.JSONDecodeError):
                await send_json(send, 400, {"error": "invalid json"})
                return
            await send_json(send, 200, {"echo": payload})
            return
        if path == "/health":
            await send_json(
                send, 405, {"error": "method not allowed"}, headers=((b"allow", b"GET"),)
            )
            return
        if path == "/echo":
            await send_json(
                send,
                405,
                {"error": "method not allowed"},
                headers=((b"allow", b"POST"),),
            )
            return
        await send_json(send, 404, {"error": "not found"})


class ResponseHeaderMiddleware:
    """包装 ``send`` 的纯 ASGI middleware。"""

    def __init__(self, app: ASGIApplication, name: bytes, value: bytes) -> None:
        self.app = app
        self.name = name.lower()
        self.value = value

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message.get("type") == "http.response.start":
                message = {
                    **message,
                    "headers": [*message.get("headers", []), (self.name, self.value)],
                }
            await send(message)

        await self.app(scope, receive, send_wrapper)


class LifespanMiddleware:
    """演示 startup/shutdown；真实资源通常由框架 lifespan 管理。"""

    def __init__(self, app: ASGIApplication) -> None:
        self.app = app
        self.started = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "lifespan":
            await self.app(scope, receive, send)
            return
        while True:
            message = await receive()
            if message.get("type") == "lifespan.startup":
                self.started = True
                await send({"type": "lifespan.startup.complete"})
            elif message.get("type") == "lifespan.shutdown":
                self.started = False
                await send({"type": "lifespan.shutdown.complete"})
                return
            else:
                raise RuntimeError(f"unexpected lifespan message: {message.get('type')!r}")


@dataclass(frozen=True, slots=True)
class ASGIResponse:
    status: int
    headers: tuple[tuple[bytes, bytes], ...]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)

    def header(self, name: str) -> str | None:
        expected = name.lower().encode("ascii")
        values = [value for key, value in self.headers if key.lower() == expected]
        return values[-1].decode("latin-1") if values else None


async def call_http_app(
    app: ASGIApplication,
    *,
    method: str = "GET",
    path: str = "/",
    body_chunks: Sequence[bytes] = (),
    headers: Sequence[tuple[bytes, bytes]] = (),
) -> ASGIResponse:
    """进程内 ASGI 测试驱动器：不启动服务器，也不创建 socket。"""

    chunks = list(body_chunks) or [b""]
    incoming = deque(
        {
            "type": "http.request",
            "body": chunk,
            "more_body": index < len(chunks) - 1,
        }
        for index, chunk in enumerate(chunks)
    )
    outgoing: list[Message] = []

    async def receive() -> Message:
        if incoming:
            return incoming.popleft()
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        outgoing.append(message)

    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.5"},
        "http_version": "1.1",
        "method": method.upper(),
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "query_string": b"",
        "headers": list(headers),
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)

    if not outgoing or outgoing[0].get("type") != "http.response.start":
        raise RuntimeError("ASGI app 必须先发送一次 http.response.start")
    start = outgoing[0]
    bodies = outgoing[1:]
    if not bodies or any(message.get("type") != "http.response.body" for message in bodies):
        raise RuntimeError("http.response.start 后只能发送 http.response.body")
    for message in bodies[:-1]:
        if not message.get("more_body", False):
            raise RuntimeError("more_body 为假后不能继续发送响应 body")
    if bodies[-1].get("more_body", False):
        raise RuntimeError("ASGI app 返回前必须结束响应 body")
    return ASGIResponse(
        status=start["status"],
        headers=tuple(start.get("headers", [])),
        body=b"".join(message.get("body", b"") for message in bodies),
    )


app = LifespanMiddleware(ResponseHeaderMiddleware(JSONEchoApp(), b"x-course", b"asgi"))
