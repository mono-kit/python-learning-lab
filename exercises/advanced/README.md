# 高级课程练习

这些文件故意保留 `TODO`。请一次只完成一章，并只运行对应测试：

```bash
pytest learning_tests/test_10_data_model.py
```

主测试目录是 `tests/`，因此普通 `pytest` 不会因为尚未学习的 TODO 失败。
参考答案在 `solutions/advanced/`；先让自己的测试通过，再对照实现。

HTTP 与 ASGI 专题需要 Web extra：

```bash
uv sync --extra dev --extra web
uv run pytest learning_tests/test_21_http_stdlib.py
```

第 21～26 章依次学习标准库 HTTP、同步客户端、异步客户端、可靠性策略、原生 ASGI 和
FastAPI 服务适配。完整讲义见 `docs/http-and-asgi.md`。
