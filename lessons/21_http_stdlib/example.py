"""第 21 章：使用 Python 标准库发送请求并实现本地 HTTP 服务。"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any, cast
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

MAX_BODY_BYTES = 1_000_000


class HTTPStatusFailure(RuntimeError):
    """服务器给出了完整 HTTP 响应，但状态码不是 2xx。"""

    def __init__(self, response: JSONResponse) -> None:
        self.response = response
        super().__init__(f"HTTP {response.status}")


@dataclass(frozen=True, slots=True)
class JSONResponse:
    """把标准库响应中最常用的部分保存成与连接无关的值对象。

    ``headers`` 是为了课程调用方便而提供的单值映射视图。它不保留重复字段，
    因而不能替代协议层的原始 header 列表；需要处理 ``Set-Cookie`` 等重复字段时，
    应直接使用客户端库提供的多值 header 类型。
    """

    status: int
    headers: Mapping[str, str]
    body: bytes

    def json(self) -> Any:
        """解析 JSON；损坏内容继续抛出 ``JSONDecodeError``。"""

        return json.loads(self.body)

    def raise_for_status(self) -> None:
        if not 200 <= self.status < 300:
            raise HTTPStatusFailure(self)


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: object | None = None,
    timeout: float = 2.0,
) -> JSONResponse:
    """用 ``urllib.request`` 发送 JSON 请求。

    ``HTTPError`` 仍包含一份合法的 HTTP 响应，因此这里把 4xx/5xx 也转换为
    ``JSONResponse``。DNS、拒绝连接等传输错误则继续以 ``URLError`` 抛出。
    """

    if timeout <= 0:
        raise ValueError("timeout 必须大于零")

    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    request = Request(url, data=body, headers=headers, method=method.upper())
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as error:
        response = error

    try:
        status = response.code if isinstance(response, HTTPError) else response.status
        return JSONResponse(
            status=status,
            # 教学适配器有意折叠成单值映射；这会丢失重复 header。
            headers=dict(response.headers.items()),
            body=response.read(),
        )
    finally:
        response.close()


class LearningHTTPHandler(BaseHTTPRequestHandler):
    """只用于课程和本地测试的微型 JSON API。"""

    protocol_version = "HTTP/1.1"
    server_version = "PythonLearningHTTP/1.0"

    def do_GET(self) -> None:
        target = urlsplit(self.path)
        if target.path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
            return
        if target.path == "/items":
            values = parse_qs(target.query).get("id")
            if not values:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "missing id"})
                return
            self._send_json(HTTPStatus.OK, {"id": values[0]})
            return
        if target.path == "/echo":
            self._method_not_allowed("POST")
            return
        self._not_found()

    def do_POST(self) -> None:
        target = urlsplit(self.path)
        if target.path in {"/health", "/items"}:
            self._method_not_allowed("GET")
            return
        if target.path != "/echo":
            self._not_found()
            return

        content_type = self.headers.get_content_type()
        if content_type != "application/json":
            self._send_json(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                {"error": "content type must be application/json"},
            )
            return

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._send_json(HTTPStatus.LENGTH_REQUIRED, {"error": "missing content length"})
            return
        try:
            length = int(raw_length)
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid content length"})
            return
        if length < 0:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid content length"})
            return
        if length > MAX_BODY_BYTES:
            self._send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "body too large"})
            return

        try:
            payload = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid json"})
            return
        self._send_json(HTTPStatus.OK, {"echo": payload})

    def do_PUT(self) -> None:
        self._reject_unsupported_method()

    def do_DELETE(self) -> None:
        self._reject_unsupported_method()

    def log_message(self, format: str, *args: object) -> None:
        """课程测试不向 stderr 输出每一条请求。"""

    def _send_json(
        self,
        status: HTTPStatus,
        payload: object,
        *,
        headers: Sequence[tuple[str, str]] = (),
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _method_not_allowed(self, *allowed: str) -> None:
        self._send_json(
            HTTPStatus.METHOD_NOT_ALLOWED,
            {"error": "method not allowed"},
            headers=(("Allow", ", ".join(allowed)),),
        )

    def _not_found(self) -> None:
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def _reject_unsupported_method(self) -> None:
        path = urlsplit(self.path).path
        if path in {"/health", "/items"}:
            self._method_not_allowed("GET")
        elif path == "/echo":
            self._method_not_allowed("POST")
        else:
            self._not_found()


@contextmanager
def running_server() -> Iterator[str]:
    """在本机随机端口启动服务，并保证线程和 socket 都被回收。"""

    server = ThreadingHTTPServer(("127.0.0.1", 0), LearningHTTPHandler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, name="learning-http-server", daemon=True)
    thread.start()
    host, port = cast(tuple[str, int], server.server_address)
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def main() -> None:
    with running_server() as base_url:
        health = request_json(f"{base_url}/health")
        echo = request_json(
            f"{base_url}/echo",
            method="POST",
            payload={"message": "你好，HTTP"},
        )
        print(health.status, health.json())
        print(echo.status, echo.json())


if __name__ == "__main__":
    main()
