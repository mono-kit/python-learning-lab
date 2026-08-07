<!-- course-chapter: 14 -->

# 第 14 章：深入 asyncio

调用 `async def` 函数只创建协程对象，不会立刻执行函数体：

```python
async def work() -> int:
    print("start")
    await asyncio.sleep(1)
    return 42


coroutine = work()
```

协程需要被等待或包装成 Task 才会推进：

```python
result = await coroutine

# 或者登记到事件循环，让它与当前任务交替推进
task = asyncio.create_task(work())
result = await task
```

直接 `await work()` 时，当前协程会等待 `work()` 完成后再继续。`create_task()`
先把协程登记为独立 Task，调用方和它可以在后续可暂停的 `await` 处交替执行。

事件循环通常在一个线程中使用协作式调度：

```text
Task A 执行 → 遇到 await，暂停
Task B 执行 → 遇到 await，暂停
Task A 等待的事件就绪 → 恢复 A
```

`await asyncio.sleep(0)` 可以主动让出一次执行权。因此：

```python
task = asyncio.create_task(worker())
await asyncio.sleep(0)
print("main resumes")
```

通常会先让 `worker` 运行到它自己的第一个暂停点，再恢复当前任务。

把普通 CPU 循环放进 `async def` 不会自动变成异步。如果长时间没有可暂停的
`await`，它会持续占用事件循环，其他 Task、超时和取消都无法及时运行。

## 14.2 取消是一种协作式异常

```python
task.cancel()
```

发出的是取消请求，不是立即强行终止任务。任务在下一次可取消的 `await` 处收到：

```python
asyncio.CancelledError
```

```python
async def worker() -> None:
    print("worker start")
    try:
        await asyncio.sleep(10)
        print("worker done")
    finally:
        print("worker cleanup")
```

在 `sleep()` 期间取消后：

```text
sleep() 处注入 CancelledError
→ 跳过 worker done
→ 执行 finally 中的 cleanup
→ CancelledError 继续向等待者传播
```

资源清理应放在 `finally` 或上下文管理器中。如果需要捕获取消来记录日志或补充
清理，通常必须重新抛出：

```python
except asyncio.CancelledError:
    cleanup()
    raise
```

在本课程环境中，`CancelledError` 继承 `BaseException`，而不是
`Exception`：

```python
issubclass(asyncio.CancelledError, BaseException)  # True
issubclass(asyncio.CancelledError, Exception)      # False
```

因此执行器可以捕获普通失败而不吞掉取消：

```python
except Exception as error:
    return WorkResult(error=str(error))
```

不要为了“兜住所有错误”改成 `except BaseException`，否则外层调用者可能无法知道
任务已经被取消，结构化并发的清理和生命周期语义也可能被破坏。

## 14.3 `TaskGroup` 与结构化并发

手动 `create_task()` 后如果没有保存并等待 Task，子任务可能逃出调用方的生命周期，
异常也可能无人处理。`TaskGroup` 把所有子任务限制在明确作用域内：

```python
tasks: list[asyncio.Task[int]] = []

async with asyncio.TaskGroup() as group:
    tasks.append(group.create_task(work(1)))
    tasks.append(group.create_task(work(2)))

# 退出后，组内任务已经结束或完成清理
results = [task.result() for task in tasks]
```

退出 `async with` 前，`TaskGroup` 会等待所有子任务完成。如果一个子任务抛出未处理
的普通异常：

```text
一个子任务失败
→ TaskGroup 取消仍在运行的兄弟任务
→ 等待兄弟任务执行 finally 清理
→ 退出时抛出 ExceptionGroup
```

并发任务可能产生多个异常，所以 TaskGroup 使用 `ExceptionGroup` 聚合，并可以用
`except*` 按异常类型处理其中的叶子异常：

```python
try:
    async with asyncio.TaskGroup() as group:
        ...
except* RuntimeError as errors:
    handle(errors)
```

课程执行器选择另一种业务语义：每个 `execute()` 把 worker 的普通异常转换为
`WorkResult`。从 TaskGroup 看，Task 是正常返回，因此一个普通工作失败不会触发
兄弟任务取消；外层取消仍会传播并让 TaskGroup 取消、等待全部子任务清理。

## 14.4 Semaphore 与结果顺序

```python
semaphore = asyncio.Semaphore(max_concurrency)
```

Semaphore 保存有限数量的许可。任务使用：

```python
async with semaphore:
    value = await worker(item)
```

许可耗尽时，其他任务在进入 `async with` 时暂停；已有任务退出后释放许可，等待任务
才能继续。上下文管理器保证正常返回、普通异常、超时或取消时都能释放许可。

Semaphore 限制的是受保护工作区中的并发量，不是 Task 总数：

```text
1000 个输入
→ 仍可能创建 1000 个 Task
→ 最多 max_concurrency 个 Task 同时执行 worker
→ 其他 Task 等待许可
```

### 完成顺序与返回顺序

任务可以按照任意顺序完成，但课程在创建时按输入顺序保存 Task：

```python
for item in items:
    tasks.append(group.create_task(execute(item)))
```

退出 TaskGroup 后再按列表顺序读取：

```python
return [task.result() for task in tasks]
```

所以输入 `[3, 1, 2]` 即使按 `1、2、3` 的顺序完成，平方结果仍按输入排列为：

```python
[9, 1, 4]
```

## 14.5 超时也是取消

```python
async with asyncio.timeout(timeout):
    value = await worker(item)
```

期限到达时，timeout 上下文使用取消机制中断当前等待：

```text
worker 的 await 处收到 CancelledError
→ worker 执行 finally 清理
→ 离开 timeout 上下文
→ timeout 将自己的取消转换为 TimeoutError
```

执行器在上下文外捕获 `TimeoutError`：

```python
except TimeoutError:
    return WorkResult(error="timeout", timed_out=True)
```

三种结果要明确区分：

```text
成功       → value=结果, error=None, timed_out=False
普通失败   → value=None, error="RuntimeError: ...", timed_out=False
超时       → value=None, error="timeout", timed_out=True
外部取消   → 不生成 WorkResult，CancelledError 继续传播
```

timeout 与 Semaphore 的嵌套顺序决定时间预算包含什么。课程实现是：

```python
async with semaphore:
    async with asyncio.timeout(timeout):
        ...
```

所以先等待许可，获得许可后才开始 worker 的超时计时。如果把 timeout 放在外层，
排队等待 Semaphore 的时间也会计入期限。

超时依赖事件循环和协作点。没有 `await` 的长时间同步计算既会阻塞事件循环，也无法
及时响应取消。

## 14.6 Queue 与背压

Semaphore 不阻止程序为大量输入一次创建大量等待 Task。持续产生的数据通常适合
有界 Queue：

```python
queue: asyncio.Queue[Item] = asyncio.Queue(maxsize=10)
```

生产者：

```python
await queue.put(item)
```

消费者：

```python
item = await queue.get()
try:
    await process(item)
finally:
    queue.task_done()
```

队列满时，`put()` 会暂停生产者，直到消费者取走元素腾出空间。这种让下游处理能力
反向限制上游生产速度的机制叫背压。

每次 `put()` 会增加未完成计数；`get()` 只表示取走，不表示处理完成；消费者完成后
必须调用 `task_done()`。协调者可以：

```python
await queue.join()
```

等待未完成计数归零。忘记 `task_done()` 会让 `join()` 一直等待。

```text
Semaphore → 限制同时执行工作区的数量
Queue     → 限制等待处理的数据量，并对生产者形成背压
```

## 14.7 阻塞 I/O、CPU 工作与执行边界

普通同步函数放进 `async def` 不会自动非阻塞。只有同步接口的阻塞 I/O 可以交给
线程：

```python
result = await asyncio.to_thread(blocking_call, argument)
```

工作线程执行阻塞函数，事件循环线程可以继续运行其他 Task。它适合阻塞式 SDK、文件
或网络库。取消等待 `to_thread()` 的协程通常不能强行停止已经运行的同步函数；调用
方可以不再等待结果，但线程里的工作可能继续执行。

纯 Python CPU 密集任务通常不能仅靠线程获得多核并行收益，因为 CPython 的 GIL
限制多个线程同时执行 Python 字节码。这类工作更适合进程池或 `multiprocessing`，
代价是更高的启动、通信和序列化成本。

三个概念：

```text
并发 concurrency  → 多个任务在一段时间内交替推进，不要求真正同时运行
并行 parallelism  → 多个任务在同一时刻运行，通常使用多个 CPU 核心
异步 asynchronous → 用暂停与恢复组织等待，让 I/O 等待期间可以处理其他任务
```

典型选择：

```text
大量异步网络请求          → asyncio
只有同步接口的阻塞式 SDK  → asyncio.to_thread()
纯 Python CPU 密集计算     → 进程池
```

### 第 14 章速记

```text
调用 async 函数只创建协程；await 或 Task 才驱动执行。
取消在协作点注入 CancelledError，finally 必须完成清理。
TaskGroup 约束子任务生命周期，失败时先取消兄弟任务再聚合异常。
Semaphore 限制活跃工作数，Queue 用有限容量对生产者形成背压。
asyncio.timeout 用取消实现超时，但外部取消仍应继续传播。
异步适合等待，线程隔离阻塞 I/O，进程利用多核处理纯 Python CPU 工作。
```

### 第 14 章复习问题

1. 调用 `async def` 函数与 `create_task()` 分别发生什么？
2. 为什么长时间没有 `await` 的协程会阻塞其他任务和超时？
3. `task.cancel()` 为什么不是立即杀死任务？
4. 为什么清理代码应放在 `finally`，并让 `CancelledError` 继续传播？
5. TaskGroup 中一个未处理异常会怎样影响兄弟任务？
6. 为什么执行器把普通异常转换成 `WorkResult` 后，TaskGroup 不会失败即停？
7. Semaphore 限制的是 Task 总数还是同时执行 worker 的数量？
8. 如何在任务完成顺序不同的情况下保持输入顺序返回？
9. worker 超时时，内部和 timeout 上下文外分别看到什么异常？
10. 把 timeout 放在 Semaphore 外层会怎样改变时间预算？
11. Queue 的 `task_done()` 与 `join()` 如何配合？
12. `asyncio.to_thread()` 为什么更适合阻塞 I/O，而进程池更适合纯 Python CPU 工作？
