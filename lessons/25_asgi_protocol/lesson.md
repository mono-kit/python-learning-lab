<!-- course-chapter: 25 -->

# 第 25 章：WSGI、ASGI 与原生应用

WSGI 和 ASGI 都是“服务器如何调用 Python 应用”的接口，不是路由框架。

| 维度 | WSGI | ASGI |
|---|---|---|
| 调用形状 | `app(environ, start_response)` | `await app(scope, receive, send)` |
| 模型 | 同步 request/response | 异步连接 + 事件流 |
| 请求 body | `wsgi.input` | `http.request` 事件 |
| 响应 | status/headers + bytes iterable | `http.response.*` 事件 |
| WebSocket | 规范不支持 | 原生协议类型 |
| 生命周期 | 无统一协议 | lifespan |

WSGI 的标准定义见 [PEP 3333](https://peps.python.org/pep-3333/)，标准库还提供
[`wsgiref`](https://docs.python.org/3/library/wsgiref.html) 参考实现。把 WSGI 应用
放进 ASGI 适配器不会让其阻塞代码自动变成异步，也不会凭空获得 WebSocket 能力。

ASGI 3 应用是一个异步 callable：

```python
async def app(scope, receive, send):
    ...
```

- `scope` 保存这条连接/请求的元数据。
- `receive()` 等待服务器发来的事件。
- `send(message)` 把应用事件交回服务器。

ASGI 基础规范是 3.0；当前 HTTP/WebSocket 子规范是 2.5；lifespan 子规范是 2.0。
版本号彼此独立，也不同于 HTTP/1.1 或 HTTP/2。详见
[ASGI specification](https://asgi.readthedocs.io/en/latest/specs/main.html)、
[HTTP/WebSocket specification](https://asgi.readthedocs.io/en/latest/specs/www.html) 和
[Lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html)。

### HTTP 事件流

请求 body 不在 scope 中，因为它可能尚未到齐或非常大：

```text
server → app: http.request {body: b"...", more_body: true}
server → app: http.request {body: b"...", more_body: false}

app → server: http.response.start {status, headers}
app → server: http.response.body  {body, more_body?}
```

应用必须读到 `more_body` 为假。客户端提前断开可能得到 `http.disconnect`。HTTP scope
只活一个请求，即使底层 TCP keep-alive 继续存在；WebSocket scope 则活整个连接。

ASGI headers 是有序的 bytes 对列表，保留重复字段。服务器负责 HTTP/2 multiplexing、
chunked transfer 解码、WebSocket frame 分片和 ping/pong；应用处理的是规范事件。

### Middleware 与并发安全

ASGI middleware 本身也是 ASGI app：它包裹内层 app，并按需要包装 receive 或 send。

```text
server → outer middleware → inner app
server ← wrapped send     ← inner app
```

每个请求的 request ID、开始时间等状态必须放在 `__call__` 局部变量中。middleware 实例
会被并发请求共享，把当前请求状态写进 `self.current_request` 会发生串线。

### Lifespan 与 WebSocket

Lifespan 常用来创建/关闭连接池：

```text
lifespan.startup  → 建立数据库池和 AsyncClient → lifespan.startup.complete
lifespan.shutdown → 关闭共享资源               → lifespan.shutdown.complete
```

通常每个事件循环、每个 worker 都会运行自己的 lifespan；不能假设只在整个部署中执行一次。

WebSocket 的基础状态机是：

```text
receive websocket.connect
send    websocket.accept
receive websocket.receive ↔ send websocket.send
receive websocket.disconnect
```

```bash
uv run pytest lessons/25_asgi_protocol/test_lesson.py
```
