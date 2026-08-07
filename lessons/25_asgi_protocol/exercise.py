"""第 25 章练习：从 scope、receive、send 实现原生 ASGI 应用。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Protocol

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class ASGIApplication(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


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


class ResponseHeaderMiddleware:
    """在 HTTP 响应开始事件中追加一个 header。"""

    def __init__(self, app: ASGIApplication, name: bytes, value: bytes) -> None:
        self.app = app
        self.name = name.lower()
        self.value = value

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # TODO: 只包装 HTTP 的 send；其他 scope 原样交给内层 app。
        # 请求相关状态必须放在本次 __call__ 的局部变量中。
        raise NotImplementedError


class LifespanMiddleware:
    """处理 startup/shutdown，并把其他 scope 交给内层应用。"""

    def __init__(self, app: ASGIApplication) -> None:
        self.app = app
        self.started = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # TODO: 持续读取 lifespan 事件；依次发送 startup.complete 和 shutdown.complete。
        raise NotImplementedError
