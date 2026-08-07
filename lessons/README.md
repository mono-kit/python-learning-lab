# Python 课程目录

每一章都在独立目录中保存 `lesson.md`、示例、练习、参考实现和验收测试。当前学习进度以
[`course.toml`](../course.toml) 为准；不要根据目录数量猜测下一课。

| 章节 | 主题 | 课件 |
|---|---|---|
| 1 | 基础语法 | [`01_basics/lesson.md`](01_basics/lesson.md) |
| 2 | Python 容器 | [`02_collections/lesson.md`](02_collections/lesson.md) |
| 3 | 函数 | [`03_functions/lesson.md`](03_functions/lesson.md) |
| 4 | 面向对象 | [`04_oop/lesson.md`](04_oop/lesson.md) |
| 5 | 异常与上下文管理器 | [`05_errors/lesson.md`](05_errors/lesson.md) |
| 6 | 迭代器与生成器 | [`06_iterators/lesson.md`](06_iterators/lesson.md) |
| 7 | 异步编程入门 | [`07_async/lesson.md`](07_async/lesson.md) |
| 8 | 常用标准库 | [`08_stdlib/lesson.md`](08_stdlib/lesson.md) |
| 9 | Pydantic 2 | [`09_pydantic/lesson.md`](09_pydantic/lesson.md) |
| 10 | 数据模型 | [`10_data_model/lesson.md`](10_data_model/lesson.md) |
| 11 | 属性协议、描述器与 MRO | [`11_descriptors/lesson.md`](11_descriptors/lesson.md) |
| 12 | 高级类型标注 | [`12_typing/lesson.md`](12_typing/lesson.md) |
| 13 | 流式处理与资源管理 | [`13_streaming/lesson.md`](13_streaming/lesson.md) |
| 14 | 深入 asyncio | [`14_concurrency/lesson.md`](14_concurrency/lesson.md) |
| 15 | 深入 pytest | [`15_testing/lesson.md`](15_testing/lesson.md) |
| 16 | 模块、打包、发布与工具 | [`16_packaging/lesson.md`](16_packaging/lesson.md) |
| 17 | 架构与可观测性 | [`17_architecture/lesson.md`](17_architecture/lesson.md) |
| 18 | SQLite 与事务 | [`18_sqlite/lesson.md`](18_sqlite/lesson.md) |
| 19 | 性能与诊断 | [`19_performance/lesson.md`](19_performance/lesson.md) |
| 20 | 本地任务队列综合项目 | [`20_task_queue/lesson.md`](20_task_queue/lesson.md) |
| 21 | HTTP 语义与标准库 | [`21_http_stdlib/lesson.md`](21_http_stdlib/lesson.md) |
| 22 | 同步 HTTP 客户端 | [`22_http_clients/lesson.md`](22_http_clients/lesson.md) |
| 23 | 异步 HTTP 与流式响应 | [`23_async_http/lesson.md`](23_async_http/lesson.md) |
| 24 | HTTP 可靠性工程 | [`24_http_resilience/lesson.md`](24_http_resilience/lesson.md) |
| 25 | WSGI、ASGI 与原生应用 | [`25_asgi_protocol/lesson.md`](25_asgi_protocol/lesson.md) |
| 26 | ASGI 服务工程 | [`26_asgi_service/lesson.md`](26_asgi_service/lesson.md) |

普通章节运行 `uv run pytest lessons/<章节>/test_lesson.py`。第 20 章使用
`lessons/20_task_queue/tests/` 中的分阶段测试。各章参考实现的位置以 `course.toml` 的
`solution` 字段为准；跨章复用代码集中在 `_shared/`，不会在多个章节复制。
