<!-- review-chapter: 7 -->

# 第 7 章快速复习：异步编程入门

## 一分钟速记

- 调用 `async def` 只创建 coroutine 对象。
- `await` 等待结果，并在可暂停点把控制权还给事件循环。
- `create_task()` 把 coroutine 安排为可并发推进的 Task。
- 并发表示交错推进，不等于多核并行。
- `async for` 每轮执行 `await anext(iterator)`，直到 `StopAsyncIteration`。
- `asyncio.run(main())` 创建并管理最外层事件循环。

```python
async with asyncio.TaskGroup() as group:
    task = group.create_task(fetch_user(1))
```

## 易错点

`async def` 中没有可暂停 `await` 的长计算仍会阻塞事件循环。TaskGroup 退出前会等待所有
子任务；一个子任务失败时，其他未完成任务会被取消。

## 快速自测

1. coroutine 与 Task 有什么区别？
2. `async for` 为什么需要等待 `__anext__()`？
3. 异步程序一定使用多个线程吗？
