<!-- course-chapter: 22 -->

# 第 22 章：同步 HTTP 客户端

讲解代码：`example.py`

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
uv run pytest lessons/22_http_clients/test_lesson.py
```
