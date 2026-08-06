"""第 25 章练习：从 scope、receive、send 实现原生 ASGI 应用。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class RequestBodyTooLarge(ValueError):
    pass


async def read_http_body(receive: Receive, *, max_bytes: int = 1_000_000) -> bytes:
    """读取所有 http.request 分块，并执行大小限制。"""

    # TODO: 不能假设一次 receive() 就得到完整 body。
    raise NotImplementedError


async def send_json(
    send: Send,
    status: int,
    payload: object,
    *,
    headers: Sequence[tuple[bytes, bytes]] = (),
) -> None:
    """依次发送 http.response.start 与 http.response.body。"""

    # TODO: JSON 编码后必须发送正确的 Content-Type 和 Content-Length。
    raise NotImplementedError


class JSONEchoApp:
    def __init__(self, *, max_body_bytes: int = 1_000_000) -> None:
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """实现 GET /health、POST /echo、400、404、405 和 413。"""

        # TODO: 不支持的 scope 类型应主动抛出异常。
        raise NotImplementedError
