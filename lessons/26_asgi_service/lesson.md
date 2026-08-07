<!-- course-chapter: 26 -->

# 第 26 章：ASGI 服务工程

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
uv run --extra web uvicorn example:app --app-dir lessons/26_asgi_service --reload
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
uv run pytest lessons/26_asgi_service/test_lesson.py
```

## 完成标准

- 能从字节、HTTP 消息、客户端库、应用协议到框架画出完整调用链。
- 能区分 HTTP status failure、transport failure、timeout、取消和数据校验失败。
- 客户端会复用连接池、显式关闭资源、限制并发，并只安全地重试。
- 标准库测试使用本机随机端口；客户端测试使用 MockTransport；ASGI 协议测试不启动网络。
- 能逐条解释 `scope`、`receive`、`send` 和 `more_body`。
- 能区分 ASGI server、framework、application、middleware 和底层协议实现。
- HTTP 路由只做边界适配，领域规则和存储仍能被 CLI、测试与其他入口复用。
