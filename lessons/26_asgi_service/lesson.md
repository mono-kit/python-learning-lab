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

## FastAPI 核心实践

### 应用入口与参数来源

命令中的 `module:application` 分别表示可导入模块和该模块中的 ASGI 应用对象：

```bash
uvicorn main:app
```

FastAPI 根据路由声明决定参数来自哪里：

```python
@router.put("/{task_id}")
def update_task(
    task_id: int,                 # path
    payload: UpdateTaskInput,     # JSON body
    notify: bool = False,         # query
) -> TaskOutput:
    ...
```

类型转换和 Pydantic 校验发生在路由函数执行之前。`task_id=abc` 无法转换成 `int`，或
body 不符合模型约束时，业务函数不会执行，FastAPI 直接返回 422。

`response_model` 既生成 OpenAPI schema，也约束并序列化输出边界。领域对象不应直接成为
HTTP 契约；本章使用 `TaskOutput.from_domain(...)` 显式完成边界转换。

### 应用工厂与依赖注入

`create_app()` 是 composition root：默认组装内存仓库，也允许测试或部署代码注入已有的
`TaskService`。默认对象必须在每次调用工厂时新建，不能作为函数默认参数提前创建，否则
多个应用会意外共享可变状态。

```python
def create_app(service: TaskService | None = None) -> FastAPI:
    task_service = service if service is not None else TaskService(...)
    application = FastAPI(...)
    application.state.task_service = task_service
    return application
```

路由通过请求所属的 application 取得服务，而不是捕获全局单例：

```python
def get_task_service(request: Request) -> TaskService:
    return request.app.state.task_service


TaskServiceDependency = Annotated[
    TaskService,
    Depends(get_task_service),
]
```

同一个 application 的请求复用同一个服务；分别调用 `create_app()` 得到的应用拥有隔离的
默认状态。

### Router、依赖和认证

`APIRouter` 负责组合一组相关路由。`prefix="/tasks"` 统一路径前缀，`tags` 组织 OpenAPI
文档；`include_router()` 才把路由注册到应用。

请求头依赖可以同时完成解析和认证：

```python
APIKeyHeader = Annotated[
    str | None,
    Header(alias="X-API-Key"),
]


def require_api_key(api_key: APIKeyHeader = None) -> None:
    if api_key != "learning-secret":
        raise HTTPException(status_code=401, detail="invalid API key")
```

只需要依赖的检查效果、不需要返回值时，使用路由的 `dependencies` 参数：

```python
@router.post("", dependencies=[Depends(require_api_key)])
def add_task(...):
    ...
```

本章只保护写接口，读取接口保持公开。这只是为了学习依赖机制的简化 API Key，不是生产
级身份系统；真实系统还要考虑密钥存储、轮换、主体身份、权限和审计。

### 请求的完整执行顺序

一次成功请求可以压缩成：

```text
HTTP request
  → middleware 请求阶段
  → 路由匹配
  → 解析 path/query/header/body
  → 执行 Depends 依赖图
  → 调用 endpoint
  → response_model 校验与序列化
  → middleware 响应阶段
  → HTTP response
```

认证依赖抛出 `HTTPException` 后，endpoint 不再执行，但框架会把异常转换成 response，响应
仍会经过外层 middleware。因此 401、404 等响应也可以统一附加 `X-Application` header。

本章的边界映射是：

| 场景 | HTTP 状态 |
|---|---:|
| 创建成功 | 201 |
| API Key 缺失或错误 | 401 |
| 任务不存在 | 404 |
| 状态转换冲突 | 409 |
| Pydantic 输入校验失败 | 422 |

### Middleware 与 lifespan

middleware 包裹每次 HTTP 请求，适合统一 header、日志、计时和 trace id。它的
`call_next(request)` 才会继续执行内层应用：

```python
@application.middleware("http")
async def add_application_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Application"] = "task-service"
    return response
```

lifespan 管理整个 application 的启动和关闭，不是每个请求执行一次：

```python
@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    await open_resources()
    try:
        yield
    finally:
        await close_resources()
```

`yield` 之前是 startup，`yield` 之后是 shutdown；`finally` 保证取消或异常时仍尝试清理。
数据库连接池、共享 HTTP client 等应用级资源适合放在这里。请求级资源则适合使用带
`yield` 的 dependency。

### 进程内测试和依赖替换

`httpx.ASGITransport` 直接调用 ASGI application，不打开 socket，适合快速验证 HTTP
边界。它不会自动执行 lifespan；需要验证生命周期时使用 `TestClient` 上下文：

```python
with TestClient(application) as client:
    assert application.state.lifecycle_events == ["startup"]
    client.get("/tasks")

assert application.state.lifecycle_events == ["startup", "shutdown"]
```

测试可以按 callable identity 替换依赖：

```python
application.dependency_overrides[require_api_key] = bypass_api_key
try:
    response = await client.post("/tasks", json={"title": "learn"})
finally:
    application.dependency_overrides.clear()
```

字典的键必须是路由注册时使用的同一个函数对象；重新加载文件得到的同名函数不是同一个
对象。验证 override 时请求应故意不带 API Key，否则即使响应成功也证明不了替换生效。

### 易错点

- 增加认证后，旧的 POST 测试也必须传合法 header；否则请求停在 401，无法继续验证
  body 的 422 或业务结果。
- `api_key` 默认值为 `None` 时，类型应写成 `str | None`，让运行时行为与类型一致。
- `dependencies=[Depends(check)]` 用于只关心检查副作用的依赖；路由需要返回值时，应把
  `Annotated[..., Depends(...)]` 声明为函数参数。
- `httpx.ASGITransport` 的无网络测试不等于真实 Uvicorn smoke test；后者还会验证导入
  路径、socket、server 配置和真实生命周期。
- 同步阻塞工作不会因为放进 `async def` 自动变成非阻塞；必须选择同步 endpoint、线程
  隔离或真正的异步实现。

### 快速自测

1. 为什么非法 path 或 body 会让 endpoint 完全不执行？
2. 为什么两个 `create_app()` 不应共享默认 `MemoryTaskRepository`？
3. `Depends` 返回值注入与 `dependencies=[...]` 的区别是什么？
4. 为什么认证失败的 401 响应仍能带上 middleware 添加的 header？
5. 为什么 `ASGITransport` 测试看不到 startup/shutdown？
6. 为什么 override 必须使用注册路由时的同一个函数对象？
7. lifespan 和带 `yield` 的请求依赖分别管理什么生命周期？

当前核心 FastAPI 实践已经完成。正式课程进度仍停在第 15 章；学完第 21～25 章的 HTTP、
可靠性与 ASGI 协议后，再回来完成真实 Uvicorn smoke test 和整条协议调用链验收。

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
uv run --extra web pytest lessons/26_asgi_service/test_lesson.py
```

## 完成标准

- 能从字节、HTTP 消息、客户端库、应用协议到框架画出完整调用链。
- 能区分 HTTP status failure、transport failure、timeout、取消和数据校验失败。
- 客户端会复用连接池、显式关闭资源、限制并发，并只安全地重试。
- 标准库测试使用本机随机端口；客户端测试使用 MockTransport；ASGI 协议测试不启动网络。
- 能逐条解释 `scope`、`receive`、`send` 和 `more_body`。
- 能区分 ASGI server、framework、application、middleware 和底层协议实现。
- HTTP 路由只做边界适配，领域规则和存储仍能被 CLI、测试与其他入口复用。
