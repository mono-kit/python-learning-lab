<!-- review-chapter: 14 -->

# 第 14 章快速复习：深入 asyncio

## 一分钟速记

- 取消会在下一个可取消的 `await` 处注入 `CancelledError`。
- 清理放在 `finally`，完成清理后通常继续传播取消。
- `TaskGroup` 管理子任务生命周期；一个失败会取消同组未完成任务。
- TaskGroup 的多个错误可能组成 `ExceptionGroup`，用 `except*` 分类处理。
- Semaphore 限制同时运行量，不保证结果顺序。
- Queue 的有界容量对生产者形成背压。
- `asyncio.to_thread()` 隔离阻塞 I/O；CPU 密集工作通常考虑进程池。
- timeout 本质上通过取消实现，超时后也必须等待清理完成。

```python
async with asyncio.timeout(0.1):
    await operation()
```

## 易错点

不要用 `except BaseException` 把取消包装成普通失败。并发完成顺序可以是 3、1、2，但若
接口承诺输入顺序，最终 results 仍应按原索引重排。

## 快速自测

1. Task 被取消后 `finally` 是否执行？
2. Semaphore 和 Queue 分别控制什么？
3. 阻塞 I/O、纯 Python CPU 工作分别适合线程还是进程？
