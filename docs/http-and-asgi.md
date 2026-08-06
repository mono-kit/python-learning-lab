# Python HTTP 与 ASGI 专题

这份讲义对应第 21～26 章。目标不是背某个框架的装饰器，而是先看懂 HTTP 消息，
再理解客户端和服务器各自管理哪些资源，最后从 ASGI 协议走到可测试的 Web API。

## 学习地图

| 章节 | 主题 | 实际产出 |
|---|---|---|
| 21 | HTTP 语义与标准库 | `urllib.request` 客户端和本地 JSON 服务 |
| 22 | 同步客户端与库生态 | 复用连接池的 HTTPX JSON 客户端 |
| 23 | 异步客户端与流式 I/O | 有界并发请求和流式摘要 |
| 24 | HTTP 可靠性工程 | timeout、有限重试、退避、幂等与安全边界 |
| 25 | WSGI、ASGI 与原生应用 | 不依赖框架的 ASGI app、middleware 和测试驱动器 |
| 26 | ASGI 服务工程 | FastAPI + Uvicorn 形式的任务 API |

安装可选 Web 技术栈：

```bash
uv sync --extra dev --extra web
```

课程测试只访问进程内应用或 `127.0.0.1` 的随机端口，不依赖公网。

## 21. HTTP 语义与 Python 标准库

HTTP 是无状态的应用层协议。无论使用 HTTP/1.1、HTTP/2 还是 HTTP/3，应用层仍在
讨论“客户端针对某个资源发送请求，服务器返回响应”。协议语义的权威定义是
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)。

### 一次请求中有什么

```text
请求：method + target + version + headers + 可选 body
响应：version + status + reason + headers + 可选 body
```

例如 JSON 并不是另一种传输协议，它只是 body 的一种表示格式：

```http
POST /echo HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 17

{"message":"hi"}
```

需要分清以下概念：

- URL 指出 scheme、host、port、path、query 和 fragment；fragment 不会发给服务器。
- method 表达操作语义。GET/HEAD 是安全方法；PUT/DELETE 在规范语义上是幂等方法，
  但这不保证某个业务实现真的正确遵守。
- `Content-Type` 描述 body 的媒体类型，`Content-Length` 描述字节数，不是字符数。
- status 是服务器对本次请求的结果分类；404/503 仍然是成功收到的 HTTP 响应，
  与 DNS 失败、拒绝连接、TLS 失败等 transport error 不同。
- headers 可能重复，名称不区分大小写；不能在所有协议层都草率地转成普通 `dict`。

### 标准库客户端分层

| 模块 | 所处层次 | 适合学习什么 |
|---|---|---|
| `urllib.parse` | URL 编解码 | query、path、相对 URL 与百分号编码 |
| `http.client` | 连接和 HTTP/1.x 消息 | host 与 request target、响应流、连接复用条件 |
| `urllib.request` | 高层同步 URL 客户端 | Request、redirect、proxy、auth、cookie handler |

`http.client` 让调用者显式创建 `HTTPConnection`/`HTTPSConnection`，发送 method、path、
headers 和 body，再读取 `HTTPResponse`。它适合下钻协议，但没有现代业务客户端常见的
JSON、连接池和统一可靠性抽象。官方文档见
[`http.client`](https://docs.python.org/3/library/http.client.html)。

`urllib.request` 构建在它之上。`urlopen(..., timeout=...)` 是同步阻塞调用，返回的对象
既是上下文管理器也是 file-like response。4xx/5xx 会以 `HTTPError` 抛出，而
`HTTPError` 本身仍携带 status、headers 和 body；DNS 等失败通常是 `URLError`。
标准库文档还说明它的 HTTP/1.1 请求使用 `Connection: close`，所以不要把 opener
误认为连接池。详见
[`urllib.request`](https://docs.python.org/3/library/urllib.request.html)。

课程实现 `request_json()` 时有意把 `HTTPError` 还原为响应值，让调用方明确选择：

```python
response = request_json(url)
if response.status == 404:
    ...
response.raise_for_status()
```

transport failure 仍继续抛出，因为此时根本没有 HTTP 响应可以读取。

### 标准库服务端

`ThreadingHTTPServer` 接收 TCP 连接，并为请求创建 handler；
`BaseHTTPRequestHandler` 解析请求行和 headers，然后调用 `do_GET()`、`do_POST()`
等方法。handler 通过 `rfile` 读取请求字节，通过 `wfile` 写响应字节：

```text
socket
  → HTTPServer 接收连接
  → BaseHTTPRequestHandler 解析消息
  → do_GET / do_POST 路由与业务处理
  → send_response / send_header / end_headers
  → wfile 写 body
```

使用 HTTP/1.1 持久连接时，必须正确界定响应 body，例如发送准确的
`Content-Length`。请求 body 也不能无限读取，要校验长度上限和媒体类型。

本章使用 `("127.0.0.1", 0)`：只绑定本机，并让操作系统选择空闲端口。测试结束时
依次执行 `shutdown()`、`server_close()` 并回收线程。

> `http.server` 官方明确说明不推荐用于生产，只实现基本安全检查。它适合协议学习、
> 本地工具和测试服务器，不是生产 Web 框架。参见
> [`http.server`](https://docs.python.org/3/library/http.server.html)。

运行：

```bash
uv run python -m python_learning_lab.web.http_stdlib
uv run pytest learning_tests/test_21_http_stdlib.py
```

## 22. 同步客户端与库生态

标准库让我们看见 HTTP，但实际工程通常还需要连接池、结构化 timeout、认证、cookie、
代理、流式传输和更一致的异常模型。

| 库 | 定位 | 调用模型 | 关键资源 |
|---|---|---|---|
| Requests | 成熟、常见的高层业务客户端 | 同步 | `Session` |
| urllib3 | 连接池、timeout、retry 等传输能力 | 同步 | `PoolManager` |
| HTTPX | Requests 风格，支持同步和异步、HTTP/2 | 两者 | `Client` / `AsyncClient` |
| aiohttp | asyncio 原生 client + server 生态 | 异步 | `ClientSession` |

Requests 适合维护大量既有同步代码。顶层 `requests.get()` 易用，但多次请求应复用
`Session`；Requests 默认没有 timeout，4xx/5xx 也要显式 `raise_for_status()`。
流式响应必须读完或关闭，连接才能回到池中。详见
[Requests Quickstart](https://requests.readthedocs.io/en/stable/user/quickstart/) 和
[Advanced Usage](https://requests.readthedocs.io/en/stable/user/advanced/)。

urllib3 更接近传输层：`PoolManager` 管连接池，`Timeout` 区分阶段，`Retry` 可配置
method、status、退避与 `Retry-After`。它很适合解释 Requests 之下发生什么，但不必
作为第一套业务 API。详见
[urllib3 User Guide](https://urllib3.readthedocs.io/en/stable/user-guide.html)。

本课程实践主线选 HTTPX，因为同一个响应模型可贯穿同步调用、异步调用、mock
transport 和后面的 ASGI 进程内测试。顶层函数适合少量调用，长期服务应复用 Client：

```python
with httpx.Client(base_url="https://api.example.com") as client:
    api = SyncJSONClient(client)
    user = api.get_object("/users/1")
```

资源所有权要明确：示例中的 `SyncJSONClient` 接收外部 Client，因此它不应该偷偷
关闭 Client。创建 Client 的 composition root 才管理其生命周期。HTTPX 官方说明见
[Clients](https://www.python-httpx.org/advanced/clients/)。

运行练习：

```bash
uv run pytest learning_tests/test_22_http_clients.py
```

## 23. 异步客户端、并发与流式 I/O

在 async 应用中发外部请求，应使用异步客户端；把同步 Requests 调用直接放进
`async def` 会阻塞事件循环。HTTPX 的基本形状是：

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

不要在热循环中为每个 URL 创建一个 AsyncClient。Client 保存连接池，应按一组任务或
应用 lifespan 复用并最终关闭。HTTPX 的 timeout 可区分 connect、read、write、pool；
其默认值表示网络不活动限制，不等于整个业务操作严格的墙钟 deadline。详见
[HTTPX Async Support](https://www.python-httpx.org/async/) 和
[Timeouts](https://www.python-httpx.org/advanced/timeouts/)。

批量请求会复用第 14 章知识：

```text
输入 URLs
→ Semaphore 限制在途请求
→ TaskGroup 管理任务生命周期
→ 每项转换为 FetchResult
→ 按输入顺序返回
```

只捕获本章契约规定的普通失败。外层取消不转换成普通结果，让 TaskGroup 继续取消和
清理所有子任务。

大响应不要调用一次 `response.content` 全部载入内存：

```python
async with client.stream("GET", url) as response:
    response.raise_for_status()
    async for chunk in response.aiter_bytes():
        ...
```

离开上下文会关闭响应。手动 streaming 模式则必须显式 `aclose()`，否则可能耗尽连接池。

aiohttp 是另一套成熟的 asyncio client/server 生态。它的 `ClientSession` 同样应按应用
生命周期复用，`StreamReader` 支持异步分块读取。`aiohttp.web.Application` 使用
aiohttp 自己的服务端接口，并不是可以直接交给任意 ASGI server 的 ASGI app。详见
[aiohttp Client Quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html) 和
[aiohttp Web Server](https://docs.aiohttp.org/en/stable/web.html)。

```bash
uv run pytest learning_tests/test_23_async_http.py
```

## 24. timeout、重试、幂等与安全边界

“timeout=5”通常不是一个完整策略。工程中至少要区分：

- pool timeout：等待连接池空位。
- connect timeout：建立 TCP/TLS 连接。
- write timeout：发送请求 body。
- read timeout：等待下一段响应数据。
- total deadline：整个业务操作允许消耗的总时间。

重试也不是“出错就再来一次”：

1. 连接失败往往发生在服务器收到请求前，通常比 read timeout 更容易安全重试。
2. read timeout 有歧义：服务器可能已经完成写操作，只是响应没有回来。
3. GET/HEAD 通常适合重试；POST 默认不能重放。
4. PUT/DELETE 在 HTTP 语义上幂等，但仍要确认业务实现。
5. 非幂等写请求需要 idempotency key 或服务端去重。
6. 流式请求体可能不能 rewind，因而不能再次发送。
7. 策略必须限制次数和总时间，使用指数退避与 jitter，并尊重 `Retry-After`。

HTTPX transport 自带的简单 retries 只覆盖连接错误和连接 timeout；状态码、read/write
失败等要由更上层策略处理。测试可使用 `MockTransport`，不访问真实服务：

```python
transport = httpx.MockTransport(handler)
client = httpx.Client(transport=transport)
```

HTTPX 也提供 WSGI/ASGI transport。官方说明见
[HTTPX Transports](https://www.python-httpx.org/advanced/transports/)。

基础安全边界：

- HTTPS 默认验证证书；不要用 `verify=False` 掩盖部署问题。
- 不把用户提供的任意 URL 直接交给服务端客户端，防止 SSRF；校验 scheme、host、port，
  并注意 DNS 重绑定和 redirect 后的目标。
- 为请求和响应设置大小限制，流式下载也要统计总字节数。
- secrets 不进入 URL query 和普通日志；Authorization、cookie 要脱敏。
- redirect、proxy 和环境变量都是信任边界，不是无害的便利功能。

```bash
uv run pytest learning_tests/test_24_http_resilience.py
```

## 25. 从 WSGI 到 ASGI

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
uv run pytest learning_tests/test_25_asgi_protocol.py
```

## 26. ASGI 服务器、框架与服务工程

先把生态分层，避免把所有项目都叫“框架”：

| 层 | 常见实现 | 职责 |
|---|---|---|
| ASGI server | Uvicorn、Hypercorn、Daphne、Granian | socket、HTTP/WebSocket 协议与 worker |
| toolkit/framework | Starlette、FastAPI、Django ASGI、Litestar | 路由、request/response、middleware、应用抽象 |
| 接口工具 | asgiref | ASGI/WSGI 适配、同步/异步桥接、类型 |
| 底层协议库 | h11、httptools、wsproto 等 | HTTP/1.1 或 WebSocket 状态机/解析 |

[Uvicorn](https://www.uvicorn.org/) 是本课程实际运行服务器；它不提供业务路由和
Pydantic 校验。[Hypercorn](https://hypercorn.readthedocs.io/en/latest/) 支持更多
协议/事件循环组合，适合验证 server 可替换性；
[Daphne](https://github.com/django/daphne) 起源于 Django Channels。

[Starlette](https://www.starlette.io/) 是轻量 ASGI toolkit；
[FastAPI](https://fastapi.tiangolo.com/) 在 Starlette 上加入 Pydantic 数据边界、
依赖注入与 OpenAPI。课程先手写原生 ASGI，再使用 FastAPI，才能看清框架替你完成了什么。

第 26 章把第 17/20 章的 `TaskService` 接到 HTTP：

```text
HTTP JSON
  → FastAPI / Pydantic 边界
  → TaskService 用例
  → TaskRepository port
  → Memory 或 SQLite adapter
```

路由不直接操作仓库，也不复制状态机规则。`TaskNotFound` 转成 404，非法状态变化转成
409，Pydantic 输入失败由框架转成 422。同步 SQLite 不会因为路由写成 `async def`
就自动变成异步；应使用同步 endpoint、线程隔离，或真正的异步存储适配器。

开发运行：

```bash
uv run --extra web uvicorn python_learning_lab.web.service_api:app --reload
```

进程内测试不启动 socket：

```python
transport = httpx.ASGITransport(app=app)
async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
    response = await client.post("/tasks", json={"title": "learn ASGI"})
```

HTTPX 明确说明 `ASGITransport` 不负责触发 lifespan；需要生命周期的测试应使用相应的
lifespan manager，或使用框架 TestClient 的上下文管理器。真实 Uvicorn smoke test 只需
保留少量，用来验证导入路径、socket 和服务器配置。

```bash
uv run pytest learning_tests/test_26_task_api.py
```

## 完成标准

- 能从字节、HTTP 消息、客户端库、应用协议到框架画出完整调用链。
- 能区分 HTTP status failure、transport failure、timeout、取消和数据校验失败。
- 客户端会复用连接池、显式关闭资源、限制并发，并只安全地重试。
- 标准库测试使用本机随机端口；客户端测试使用 MockTransport；ASGI 协议测试不启动网络。
- 能逐条解释 `scope`、`receive`、`send` 和 `more_body`。
- 能区分 ASGI server、framework、application、middleware 和底层协议实现。
- HTTP 路由只做边界适配，领域规则和存储仍能被 CLI、测试与其他入口复用。
