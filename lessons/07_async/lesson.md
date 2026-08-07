<!-- course-chapter: 7 -->

# 第 7 章：异步编程入门

文件：`example.py`

```python
async def fetch_user(...):
    await asyncio.sleep(...)
    return user
```

调用协程函数只会创建协程对象：

```python
coroutine = fetch_user(1)
```

使用 `await` 才会等待并取得结果：

```python
user = await fetch_user(1)
```

`await` 会暂停当前协程，把执行权交还给事件循环。

### 并发任务

```python
async with asyncio.TaskGroup() as group:
    task = group.create_task(fetch_user(1))
```

- coroutine 是异步工作说明。
- Task 是已交给事件循环调度的工作。
- 并发不等于多核并行。

### 异步生成器

```python
async def ticker():
    await ...
    yield value
```

通过 `async for` 消费：

```python
async for value in ticker():
    ...
```

`async for` 概念上相当于：

```python
iterator = aiter(values)

while True:
    try:
        value = await anext(iterator)
    except StopAsyncIteration:
        break
```

最外层入口：

```python
asyncio.run(main())
```

### 调度、并发与清理

事件循环让任务在遇到可暂停的 `await` 时合作切换；没有 `await` 的长时间同步计算仍会
阻塞整个线程。`await coroutine` 会等待一个工作完成，`create_task()` 才会把协程安排成
可与当前任务并发推进的 Task。

`TaskGroup` 形成结构化生命周期：离开上下文前所有子任务都必须结束；一个子任务失败时，
其他未完成任务会被取消，错误在退出处汇总。清理应放进 `finally`，不要把
`CancelledError` 当成普通失败吞掉。

异步生成器的 `async for` 每轮调用并等待 `__anext__()`；遇到
`StopAsyncIteration` 正常结束。因此“异步”表示取下一项可能等待，并不表示多线程。
完成练习后运行：

```bash
uv run pytest lessons/07_async/test_lesson.py -q
```
