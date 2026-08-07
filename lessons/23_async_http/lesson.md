<!-- course-chapter: 23 -->

# 第 23 章：异步 HTTP 与流式响应

讲解代码：`example.py`

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
uv run pytest lessons/23_async_http/test_lesson.py
```
