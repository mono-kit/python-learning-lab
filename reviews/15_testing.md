<!-- review-chapter: 15 -->

# 第 15 章快速复习：深入 pytest

## 一分钟速记

- 测试按 Arrange、Act、Assert 组织，优先验证返回值和最终状态；调用方式本身是契约时
  才验证交互。
- pytest 按参数名解析 fixture，而不是按类型标注；同一个测试中，function-scoped
  fixture 即使经过多条依赖路径请求也只创建一次。
- `FrozenClock` 固定时间，`MemoryAuditSink` 提供可查询状态的 fake，让业务测试不依赖
  真实时间和外部存储。
- `@pytest.mark.parametrize` 把一条规则展开成多个独立测试项；`pytest.raises` 同时验证
  异常类型和稳定的业务信息。
- `tmp_path` 隔离文件系统，`monkeypatch` 临时控制环境变量，`caplog` 捕获日志事件；它们
  都会由 pytest 管理生命周期。
- fake 做简化但真实的事情，适合观察最终状态；`Mock(spec=...)` 记录调用，适合验证边界
  交互，但 `spec` 不会完成静态类型检查。
- 调用协程函数只创建协程对象；`create_task()` 把协程包装成 Task 并安排执行，`await`
  才等待它完成并取得最终结果。
- `Task.cancel()` 只发出取消请求。继续 `await task` 才能观察 `CancelledError`，并等待
  `TaskGroup` 中的子任务执行 `finally` 清理。

## 关键执行模型

```text
run_limited(...)             → 创建协程对象，函数体尚未运行
create_task(coroutine)       → 创建并调度 Task
当前测试遇到等待中的 await   → 事件循环获得机会运行 Task
task.cancel()                → 请求在可取消点注入 CancelledError
await task                   → 等待取消传播和 finally 清理完成
```

异步测试用 `Event` 表达真实先后关系：`started` 保证 worker 已启动，未设置的 `release`
让 worker 稳定停在可取消点，`cleanup_finished` 证明 `finally` 已完成。不要用较长
`sleep()` 猜测调度时机。

## 易错点

- fixture 参数的类型标注不参与注入，拼错参数名会导致 fixture 查找失败。
- 不要让多个测试共享可变的 session-scoped fake，也不要让测试依赖执行顺序。
- JSONL 测试应解析字段，不要绑定空格或字段顺序；日志测试应检查事件名和结构化字段，
  不要比较包含时间戳的完整格式文本。
- `Mock(spec=AuditSink)` 能阻止访问不存在的属性，但不保证所有实参的静态类型正确。
- `asyncio.Event.set()` 只唤醒等待者，不会立即切换任务；当前协程通常继续运行到下一个
  需要等待的 `await`。
- 当前 Python 中 `asyncio.CancelledError` 不属于普通 `Exception`，因此不要假设
  `except Exception` 会把取消转换成普通失败。

## 快速自测

1. pytest 为什么能把同一个 `memory_sink` 同时交给服务 fixture 和测试函数？
2. 参数化测试里的 fixture 参数与案例参数分别从哪里获得？
3. fake 的状态断言与 mock 的交互断言各自会发现什么问题？
4. `tmp_path`、`monkeypatch` 和 `caplog` 分别控制哪个外部边界？
5. 为什么调用异步函数得到的是协程对象，而不是函数最终返回值？
6. `execution.cancel()` 之后为什么仍然需要 `await execution`？
7. `started`、`release` 和 `cleanup_finished` 三个 Event 各自保证了什么？
