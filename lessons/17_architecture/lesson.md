<!-- course-chapter: 17 -->

# 第 17 章：架构与可观测性

这一章不追求把代码分成更多文件，而是学习如何让业务规则不被数据库、Web 框架、
Pydantic 或命令行绑死。完成后，你应该能看懂本项目的 `engineering/` 目录，并能用
内存实现测试同一套应用服务。

本章配套内容：

- 讲解代码：`lessons/_shared/task_queue/`
- 练习：`lessons/17_architecture/exercise.py`
- 验收：`lessons/17_architecture/test_lesson.py`
- 参考实现：`lessons/_shared/task_queue/domain.py`

先运行：

```bash
uv run pytest lessons/17_architecture/test_lesson.py -q
```

初始失败是练习的一部分。阅读本章时，可以同时打开
`lessons/_shared/task_queue/` 中的 `domain.py`、`ports.py`、`service.py` 和
`adapters.py`。

## 1. 架构首先是在管理变化

假设一个任务系统现在使用 SQLite，之后可能改成 PostgreSQL；现在由 CLI 调用，之后
可能增加 HTTP API。如果状态流转规则散落在 SQL、路由函数和 Pydantic validator 中，
每增加一个入口都要复制规则，也很难进行快速单元测试。

我们把变化速度不同的代码分开：

```text
外部入口（CLI / HTTP / 定时任务）
            ↓
应用服务（用例编排）
            ↓
领域模型（业务规则）
            ↑
端口 Protocol ← 适配器（内存 / SQLite / 外部 API）
```

箭头不是简单的“调用方向”，更重要的是源码依赖方向：领域层不导入外层框架；应用
服务依赖自己定义的抽象端口；外部适配器再去实现这些端口。越靠近业务规则，越不应
知道部署细节。

可以用一个问题检查边界：如果明天删除 FastAPI、Pydantic 或 SQLite，任务从
`pending` 变成 `running` 的规则是否还能原样保留？如果答案是否定的，规则可能放错了。

## 2. 领域对象负责维护自身不变量

本项目的 `Task` 是不可变值对象：

```python
@dataclass(frozen=True, slots=True)
class Task:
    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    error: str | None = None

    def start(self) -> "Task":
        self._require(TaskStatus.PENDING)
        return replace(self, status=TaskStatus.RUNNING)
```

这里有三个重要决策：

1. `__post_init__` 检查“ID 和标题不能为空”等始终成立的不变量。
2. `start()`、`fail()`、`retry()` 表达允许的状态转换，不让调用方任意改字符串。
3. `frozen=True` 让每次转换返回新对象，旧状态仍可用于审计和比较。

领域对象不需要继承框架基类，也不应该在方法里连接数据库或打印消息。它只回答：
“这个操作在当前状态是否合法，合法后得到什么新状态？”

```python
pending = Task("task-1", "build wheel")
running = pending.start()

assert pending.status is TaskStatus.PENDING
assert running.status is TaskStatus.RUNNING
```

非法转换抛出领域异常 `InvalidTransition`。这个异常描述业务含义；HTTP 层以后可以把它
翻译成 409，CLI 可以翻译成一条错误消息，但领域层不需要知道 HTTP 状态码。

## 3. Protocol 定义应用真正需要的能力

应用服务需要保存和查询任务，但它不需要知道 SQLite 的连接、表名和 SQL。于是由核心
代码定义端口：

```python
class TaskRepository(Protocol):
    def get(self, task_id: str) -> Task | None: ...
    def list(self) -> Sequence[Task]: ...
    def save(self, task: Task) -> None: ...


class IdGenerator(Protocol):
    def __call__(self) -> str: ...
```

`Protocol` 使用结构化子类型：实现类不必显式继承 `TaskRepository`，只要具有兼容的
方法签名，静态类型检查器就会接受它。这使内存仓库、SQLite 仓库和测试 fake 都能替换。

“依赖倒置”的关键不是多写一个接口文件，而是抽象由使用者拥有。`TaskService` 声明自己
需要什么，SQLite 适配器来满足它；不是应用服务被迫依赖数据库库提供的具体类型。

## 4. 应用服务只编排一个用例

领域模型处理单个对象的规则，应用服务负责跨对象和 I/O 的顺序：

```python
class TaskService:
    def __init__(self, repository: TaskRepository, generate_id: IdGenerator) -> None:
        self.repository = repository
        self.generate_id = generate_id

    def add(self, title: str) -> Task:
        task = Task(id=self.generate_id(), title=title.strip())
        self.repository.save(task)
        return task
```

`TaskService` 不在构造函数里偷偷创建 SQLite 连接，也不直接调用 `uuid4()`。这些依赖由
外面传入，因此测试能使用确定的 ID 和内存存储。

应用服务通常负责：

- 查询实体，找不到时抛出应用级错误，例如 `TaskNotFound`；
- 调用领域方法完成规则判断；
- 按用例要求保存结果；
- 记录具有业务意义的事件。

它不负责：解析 HTTP JSON、选择终端颜色、拼 SQL、读取环境变量或配置日志 handler。

## 5. 适配器把外部世界接到端口上

内存仓库是一个真实、简单而快速的适配器：

```python
class MemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task
```

它不是通过 `Mock()` 猜测调用细节，而是实现真实语义，所以很适合服务测试。SQLite
仓库则把相同端口映射到 SQL。两者都可以传给 `TaskService`：

```python
service = TaskService(
    repository=MemoryTaskRepository(),
    generate_id=SequentialIdGenerator(),
)
task = service.add("build wheel")
```

最终程序需要一个“组合根”选择具体实现并把对象组装起来。CLI 的 `main()` 或 Web
应用的启动函数适合承担这个职责；业务类本身不应该决定使用哪个适配器。

## 6. Pydantic 应留在输入输出边界

Pydantic 非常适合解析外部数据，但 `BaseModel` 不必进入领域层。边界流程通常是：

```text
未经信任的 JSON
  → Pydantic 输入模型
  → 普通 Python 参数
  → 领域对象 / 应用服务
  → Pydantic 输出模型
  → JSON
```

例如：

```python
incoming = CreateTaskInput.model_validate({"title": "  build wheel  "})
task = service.add(incoming.title)
outgoing = TaskOutput.from_domain(task)
```

这样做的收益是领域规则可在没有 Web 框架和序列化库的环境中运行；同一个服务可以被
CLI、后台任务和 HTTP API 复用。Pydantic 的错误属于输入边界，`InvalidTransition`
属于领域边界，两者不要混成一种异常。

## 7. 异常要在理解其含义的边界上翻译

一个低层 `sqlite3.IntegrityError` 不应该直接成为用户 API 的返回内容，但也不应该在
任何地方都用 `except Exception` 吞掉。判断规则是：当前层是否能增加有用语义？

```python
try:
    service.start(task_id)
except TaskNotFound as exc:
    # HTTP 适配器可在这里翻译为 404。
    raise HTTPException(status_code=404, detail="task not found") from exc
except InvalidTransition as exc:
    # 领域冲突可以翻译为 409。
    raise HTTPException(status_code=409, detail=str(exc)) from exc
```

无法处理或无法增加语义时让异常继续传播。翻译时使用 `raise ... from exc` 保留原因链，
日志也应避免在每一层重复记录同一个异常。

## 8. 日志是事件记录，不是散落的 print

库代码获取命名 logger 并记录事件：

```python
self.logger.info(
    "task_status_changed",
    extra={"task_id": updated.id, "status": updated.status.value},
)
```

入口层才负责选择 level、handler 和 formatter：

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
```

两者职责不同：

- logger 表达“发生了什么”；
- level 表达严重程度；
- handler 决定写向终端、文件或日志平台；
- formatter 决定文本或结构化格式；
- `extra` 提供可查询的上下文，而不是把所有字段拼进一句话。

不要在可复用库中调用 `basicConfig()`，否则库会替应用决定全局日志策略。测试可用
`caplog` 观察事件，而不用真的写文件：

```python
def test_add_logs_event(caplog):
    caplog.set_level(logging.INFO)
    service.add("build wheel")
    assert "task_added" in caplog.messages
```

密码、令牌、完整请求体等敏感数据不应进入日志；日志内容也是对外边界的一部分。

## 9. 用契约测试防止适配器语义漂移

只有内存仓库测试通过，不代表 SQLite 实现一定具有相同语义。可以把共同断言抽成一个
“仓库契约”，分别传入不同实现：

```python
def repository_contract(repository: TaskRepository) -> None:
    task = Task("task-1", "build wheel")
    repository.save(task)
    assert repository.get(task.id) == task
    assert repository.list() == (task,)


def test_memory_repository_contract() -> None:
    repository_contract(MemoryTaskRepository())
```

SQLite 测试也调用同一函数，并额外测试事务、约束和持久化。这样服务层测试可以很快，
适配器层又不会因为 fake 过于理想而漏掉真实行为。

## 10. 本章练习顺序

练习文件只要求实现最核心的不可变状态机，按以下顺序完成：

1. 在 `start()` 中只接受 `PENDING`，返回 `RUNNING` 的新对象。
2. 在 `fail()` 中只接受 `RUNNING`，拒绝空白原因，并保存错误。
3. 在 `retry()` 中只接受 `FAILED`，返回 `PENDING` 并清除错误。
4. 确认每次转换后原对象没有变化。

每完成一步运行：

```bash
uv run pytest lessons/17_architecture/test_lesson.py -q
```

然后阅读完整工程示例并运行集成测试：

```bash
uv run pytest lessons/20_task_queue/tests/test_02_service.py -q
uv run mypy --strict lessons/_shared/task_queue
```

## 11. 常见误区

- **把分层等同于文件夹数量**：如果领域层仍导入数据库，移动文件没有改变依赖。
- **所有逻辑都放 service**：实体自身不变量仍应由实体维护。
- **Protocol 过大**：按用例需要拆小端口，避免每个 fake 实现无关方法。
- **测试只验证 mock 调用次数**：优先验证可观察结果和真实语义。
- **领域异常携带 HTTP 状态码**：这会让核心规则依赖一种入口协议。
- **模块导入时配置日志或连接数据库**：导入应尽量无外部副作用。

## 12. 完成标准与复习题

完成本章时，你应能做到：

- 画出领域、端口、服务、适配器和入口之间的依赖方向；
- 说明为什么 `TaskService` 接收 `TaskRepository`，却不导入 SQLite 仓库；
- 用内存 fake 测试服务，并用契约测试约束多个仓库实现；
- 区分输入校验异常、领域异常、应用异常和适配器异常；
- 说明为什么库记录日志事件，而入口配置 handler。

请口头回答：

1. `MemoryTaskRepository` 没有继承 `TaskRepository`，为什么仍可传给服务？
2. 如果新增 REST API，哪些文件应该保持完全不变？
3. 为什么“在服务内部调用 `sqlite3.connect()`”会降低可测试性？
4. `print("task added")` 与 `logger.info("task_added", extra=...)` 的边界差别是什么？
