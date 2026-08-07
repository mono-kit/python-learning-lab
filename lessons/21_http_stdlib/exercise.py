"""第 21 章练习：只用标准库完成 JSON HTTP 客户端和服务端。"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

MAX_BODY_BYTES = 1_000_000


class HTTPStatusFailure(RuntimeError):
    """服务器返回了非 2xx HTTP 响应。"""

    def __init__(self, response: JSONResponse) -> None:
        self.response = response
        super().__init__(f"HTTP {response.status}")


@dataclass(frozen=True, slots=True)
class JSONResponse:
    """简化的单值响应视图；重复 header 不在本练习的保存范围内。"""

    status: int
    headers: Mapping[str, str]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)

    def raise_for_status(self) -> None:
        """非 2xx 时抛出包含当前响应的 ``HTTPStatusFailure``。"""

        # TODO: 成功响应应直接返回；失败异常必须保留 self。
        raise NotImplementedError


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    timeout: float = 2.0,
) -> JSONResponse:
    """发送 JSON 请求；把 4xx/5xx 也转换成 JSONResponse。"""

    # TODO: 使用 Request、urlopen 和 HTTPError 实现。
    raise NotImplementedError


class LearningHTTPHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        # TODO: 实现 GET /health 和带 id query 的 /items。
        # 其他路径返回 JSON 404；已知路径的错误方法返回 405 + Allow。
        raise NotImplementedError

    def do_POST(self) -> None:
        # TODO: 实现 POST /echo；检查 Content-Type、Content-Length 与 MAX_BODY_BYTES，
        # 再读取并解析 JSON；已知路径的错误方法返回 405 + Allow。
        raise NotImplementedError

    def log_message(self, format: str, *args: object) -> None:
        pass

    def _send_json(
        self,
        status: HTTPStatus,
        payload: object,
        *,
        headers: Sequence[tuple[str, str]] = (),
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)


@contextmanager
def running_server() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), LearningHTTPHandler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
