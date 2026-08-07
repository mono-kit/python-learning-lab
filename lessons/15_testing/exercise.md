# 第 15 章练习：建立确定性的 pytest 测试矩阵

本章练习代码就是测试，文件位于：

```text
lessons/15_testing/test_lesson.py
```

先读同目录的 `example.py`，再逐个完成测试中的 TODO：

1. fixture 组合固定时间、内存 fake 与服务。
2. 参数化覆盖所有空白 action。
3. 使用 `tmp_path` 验证 JSONL 导出。
4. 使用 `monkeypatch` 控制环境变量边界。
5. 使用 `caplog` 验证结构化日志事件。
6. 使用 `Mock(spec=AuditSink)` 验证一次边界交互。
7. 使用 `asyncio.Event` 验证取消传播与 worker 的 `finally` 清理。

```bash
uv run pytest lessons/15_testing/test_lesson.py -x
```

每次只解决第一项失败。全部通过后，再对照
`reference_test.py`。第 17 章的仓库契约和第 18 章的 SQLite 集成测试
留到学完对应实现后进行，本章不会倒序依赖尚未学习的内容。

写完后解释每个 fixture 管理的是数据、资源还是行为；如果一个 fixture 同时承担三类
职责，尝试拆分。
