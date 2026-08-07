<!-- course-chapter: 13 -->

# 第 13 章：流式处理与资源管理

函数体中只要出现 `yield`，调用它时就会创建生成器对象，而不会立刻执行函数体：

```python
def numbers(limit: int) -> Iterator[int]:
    print("A")
    if limit <= 0:
        raise ValueError("invalid limit")
    yield 1


iterator = numbers(0)
print("B")
```

此时只输出 `B`。第一次执行 `next(iterator)` 才进入函数体，输出 `A`，随后抛出
`ValueError`。

生成器的基本执行过程：

```text
调用生成器函数 → 创建生成器对象，不执行函数体
第一次 next() → 从函数开头运行到第一个 yield
后续 next() → 从上一次 yield 后恢复，运行到下一个 yield
函数结束 → 抛出 StopIteration
```

`yield` 前面的参数检查也属于生成器函数体，因此同样会推迟。

### 立即校验、惰性读取

如果参数必须在调用时立即校验，而文件仍应在消费时打开，可以组合外层普通函数和
内层生成器：

```python
def validated_batches(
    path: Path,
    batch_size: int,
) -> Iterator[list[Event]]:
    if batch_size <= 0:
        raise ValueError("batch_size 必须大于零")

    def generate() -> Iterator[list[Event]]:
        with path.open(encoding="utf-8") as source:
            ...
            yield batch

    return generate()
```

外层函数没有 `yield`，所以调用时立刻执行参数检查；内层 `generate()` 包含
`yield`，所以打开文件和读取内容推迟到第一次消费。

执行边界：

```text
validated_batches(path, size)
→ 立即检查 size
→ 返回内部生成器

next(generator)
→ 打开文件
→ 读取并验证记录
→ 产出一个批次后暂停
```

## 13.2 生成器的暂停、关闭与资源生命周期

当 `yield` 位于 `with` 内部时，生成器暂停期间还没有离开 `with`，资源会继续
保持打开：

```python
def read_lines(path: Path) -> Iterator[str]:
    with path.open(encoding="utf-8") as source:
        for line in source:
            yield line
```

资源会在以下路径中清理：

```text
生成器正常耗尽 → 离开 with → 关闭资源
生成器内部异常 → 调用栈展开 → 离开 with → 关闭资源
显式 generator.close() → 注入 GeneratorExit → 离开 with → 关闭资源
```

`close()` 不是让生成器正常执行剩余代码。它近似于在暂停的 `yield` 位置抛入
`GeneratorExit`：

```python
def generate() -> Iterator[int]:
    with resource():
        print("before")
        yield 1
        print("after")
```

在第一次 `next()` 后调用 `close()`，会执行 `with` 的清理，但不会输出
`after`。提前停止消费且仍然保存生成器引用时，资源可能继续打开，因此需要明确
耗尽或关闭生成器，不能只依赖未来的垃圾回收。

## 13.3 迭代器的单次消费语义

生成器对象同时是 `Iterable` 和 `Iterator`：

```python
iterator = read_lines(path)
iter(iterator) is iterator  # True
```

它记录当前消费位置，不会在第二次遍历时自动复位：

```python
iterator = iter([10, 20, 30])

first = next(iterator)     # 10
remaining = list(iterator) # [20, 30]
again = list(iterator)     # []
```

要重新读取文件，必须重新调用函数创建新的生成器：

```python
first_run = validated_batches(path, 100)
second_run = validated_batches(path, 100)
```

返回类型 `Iterator[list[Event]]` 只描述消费接口，本身不能证明实现一定惰性。下面
的实现虽然返回迭代器，却已经提前加载全部数据：

```python
def load_all(path: Path) -> Iterator[Event]:
    events = read_everything(path)
    return iter(events)
```

真正的流式处理要求生产者逐步产出，消费者也逐步处理。调用方如果执行：

```python
all_batches = list(validated_batches(path, 100))
```

仍然会主动把全部批次收集到内存。

## 13.4 JSONL 解析、验证与异常边界

JSONL 使用一行表示一条 JSON 记录。流式管道应逐行完成：

```text
读取一行
→ 跳过空行
→ 解析 JSON
→ Pydantic 校验
→ 加入当前批次
→ 批次满时 yield
```

### `json.load()` 与 `json.loads()`

```text
json.load(file_object) → 从具有 read() 的文件对象读取 JSON
json.loads(string)     → 从字符串解析 JSON
```

文件迭代产生的 `line` 是字符串，因此使用：

```python
payload = json.loads(line)
```

### 保留真实物理行号

```python
for line_number, line in enumerate(source, start=1):
    if not line.strip():
        continue
```

先编号、再跳过空行，能够让错误行号与编辑器中的物理行号保持一致。空行虽然不产生
事件，仍然占据文件中的一行。

### 统一底层异常

每条记录可能在两个阶段失败：

```text
json.loads()          → json.JSONDecodeError
Event.model_validate → pydantic.ValidationError
```

管道把它们转换成包含路径和行号的领域异常：

```python
except (json.JSONDecodeError, ValidationError) as error:
    raise InvalidRecord(
        path=path,
        line_number=line_number,
        reason=str(error),
    ) from error
```

调用方只需处理统一的 `InvalidRecord`，同时还可以通过 `error.__cause__` 访问原始
解析或校验异常。`raise ... from error` 在提高抽象层次时保留了调试线索。

错误也遵守惰性语义：如果第一行已经凑满一批并被产出，第二行的损坏内容要到下一次
`next()` 才会读取并报错。异常发生后调用栈离开文件的 `with`，文件仍会被关闭。

## 13.5 批次对象与内存边界

批次达到目标大小时：

```python
if len(batch) == batch_size:
    yield batch
    batch = []
```

这里使用 `batch = []` 创建新列表，而不是 `batch.clear()`。`yield` 把列表对象
本身交给调用方；如果清空同一个列表，调用方已经拿到的批次也会一起变空。

文件结束时还要产出不足一个完整批次的记录：

```python
if batch:
    yield batch
```

例如三条记录、批大小为二：

```text
第一次 yield → [a, b]
最终 yield   → [c]
```

生产者逐行读取时，主要内存占用是当前行和当前批次：

```text
O(batch_size)
```

而不是与整个文件记录数一起增长。这个结论仍取决于消费者没有把所有批次重新汇总成
一个大列表。

## 13.6 `contextmanager` 与 `ExitStack`

`@contextmanager` 把“进入逻辑、一次 `yield`、退出逻辑”组织成上下文管理器：

```python
@contextmanager
def managed_resource() -> Iterator[Resource]:
    resource = acquire()
    try:
        yield resource
    finally:
        resource.close()
```

`yield` 前对应 `__enter__` 阶段，产出的值绑定给 `as` 后的变量；`yield` 后和
`finally` 对应 `__exit__` 阶段。

资源数量固定时可以直接写多个 `with`。资源数量只有运行时才知道时，使用
`ExitStack`：

```python
@contextmanager
def open_texts(paths: Sequence[Path]) -> Iterator[list[TextIO]]:
    with ExitStack() as stack:
        streams: list[TextIO] = []
        for path in paths:
            streams.append(
                stack.enter_context(path.open(encoding="utf-8"))
            )
        yield streams
```

`stack.enter_context(manager)` 调用上下文管理器的进入逻辑，并登记之后的退出逻辑。
离开 `ExitStack` 时按后进先出顺序清理：

```text
进入 A → 进入 B → 进入 C
退出 C → 退出 B → 退出 A
```

如果打开 C 时失败，已经成功打开的 B 和 A 仍会逆序关闭。这让动态数量资源在部分
建立失败时也不会泄漏。

### 第 13 章速记

```text
调用生成器只创建对象，next() 才推进到下一个 yield。
外层普通函数负责立即校验，内层生成器负责惰性读取。
with 位于生成器中时跨 yield 保持资源，耗尽、异常或 close() 才清理。
迭代器只能向前消费；流式内存优势取决于生产者和消费者双方。
JSONL 逐行解析，异常携带物理行号并通过 raise from 保留原因。
ExitStack 动态登记资源，退出时按相反顺序统一释放。
```

### 第 13 章复习问题

1. 为什么生成器函数中写在第一个 `yield` 之前的参数检查也会推迟？
2. 如何同时实现参数立即校验和文件惰性打开？
3. 生成器暂停在 `with` 中的 `yield` 时，文件为什么仍然打开？
4. `generator.close()` 为什么会执行清理，却不会执行 `yield` 后的普通代码？
5. 为什么第二次遍历同一个生成器通常得不到任何元素？
6. 为什么批次产出后应写 `batch = []`，而不是 `batch.clear()`？
7. 为什么要先用 `enumerate()` 编号，再跳过空行？
8. `raise InvalidRecord(...) from error` 保留了什么信息？
9. 为什么返回 `Iterator[list[Event]]` 不足以单独证明实现是惰性的？
10. `ExitStack` 为什么按照与进入相反的顺序清理资源？
