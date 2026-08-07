<!-- course-chapter: 21 -->

# 第 21 章：HTTP 语义与标准库

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

为让标准库练习聚焦 status 与 JSON，`HTTPResponse.headers` 暂时提供
`dict[str, str]` 的单值教学视图：名称统一成小写，重复字段只保留最后一个值。这是明确的
有损简化，不是完整 HTTP header 模型；需要处理 `Set-Cookie` 等重复字段时，应保留
有序的 `(name, value)` 列表或使用库提供的多值 header 类型。

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
uv run python lessons/21_http_stdlib/example.py
uv run pytest lessons/21_http_stdlib/test_lesson.py
```
