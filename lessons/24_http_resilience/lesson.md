<!-- course-chapter: 24 -->

# 第 24 章：HTTP 可靠性工程

讲解代码：`example.py`

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

本章的可执行部分把纯策略与真实等待拆开：`parse_retry_after()` 解析秒数或 HTTP-date，
`retry_delay_with_deadline()` 在不调用 `sleep` 的情况下综合退避、服务器提示与剩余总预算。
TLS、SSRF、redirect 和日志脱敏仍是需要结合部署环境审查的安全边界，不用一个玩具函数
假装已经自动解决。

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
uv run pytest lessons/24_http_resilience/test_lesson.py
```
