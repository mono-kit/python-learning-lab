<!-- course-chapter: 15 -->

# 第 15 章：深入 pytest

本章不是 pytest API 清单，而是学习怎样把业务规则写成稳定、清楚、失败后容易定位的
可执行例子。完成后，你应该能够判断一个测试需要检查返回值、最终状态还是边界交互，
并能避免真实时间、固定路径、全局环境和偶然调度顺序造成的不稳定测试。

## 1. 本章学习入口

讲解源码：

```text
lessons/15_testing/example.py
lessons/14_concurrency/exercise.py
```

测试练习：

```text
lessons/15_testing/test_lesson.py
```

参考测试：

```text
lessons/15_testing/reference_test.py
```

完整练习命令：

```bash
uv run pytest lessons/15_testing/test_lesson.py
```

本章的练习文件本身就是测试代码。不要为了让测试通过而修改讲解源码；测试应描述已有
接口的行为。

## 2. 测试首先是一条行为说明

一个好的测试通常回答一条具体问题：

```text
给定什么前提？
执行什么行为？
应该观察到什么结果？
```

这也叫 Arrange、Act、Assert：

```python
def test_normalizes_action() -> None:
    # Arrange：建立前提
    service = ...

    # Act：只执行本测试关注的行为
    record = service.record("  deploy  ")

    # Assert：验证这条规则的可观察结果
    assert record.action == "deploy"
```

注释不必机械保留，但结构应清楚。一个测试中如果混入许多无关行为，其中任意一项失败
都会让错误定位变困难。

### 三类常见观察

| 观察对象 | 问题 | 典型断言 |
|---|---|---|
| 返回值 | 调用得到了什么？ | `assert record.action == "deploy"` |
| 最终状态 | 系统保存了什么？ | `assert sink.records == [record]` |
| 边界交互 | 某个依赖怎样被调用？ | `sink.save.assert_called_once_with(record)` |

优先检查返回值和最终状态。只有“调用方式本身就是契约”时，才检查交互；否则测试会和
实现细节绑定得过紧。

## 3. pytest 怎样发现并执行测试

pytest 默认根据命名约定收集：

```text
test_*.py 文件
test_* 函数
Test* 类中的 test_* 方法
```

执行测试文件时，Python 首先正常导入模块。因此装饰器、模块级表达式和 fixture 定义都
发生在运行时。pytest 收集测试函数后，会检查函数签名，解析其中的 fixture 参数，再
调用测试。

例如：

```python
def test_record(audit_service, memory_sink):
    ...
```

这里的参数不是调用者手写传入，也不是 Python 根据类型标注自动注入。pytest 按名称
寻找 `audit_service` 和 `memory_sink` fixture，取得值后近似执行：

```python
test_record(
    audit_service=resolved_service,
    memory_sink=resolved_sink,
)
```

类型标注帮助读者和类型检查器理解值，不决定 pytest 选择哪个 fixture。

## 4. fixture：把测试准备过程变成依赖图

最小 fixture：

```python
@pytest.fixture
def memory_sink() -> MemoryAuditSink:
    return MemoryAuditSink()
```

fixture 也能依赖其他 fixture：

```python
@pytest.fixture
def audit_service(
    fixed_now: datetime,
    memory_sink: MemoryAuditSink,
) -> AuditService:
    return AuditService(FrozenClock(fixed_now), memory_sink)
```

pytest 会建立依赖图：

```text
fixed_now ─────┐
               ├─→ audit_service ─→ test
memory_sink ───┘          │
                          └─test 也可以直接请求 memory_sink
```

### 同一测试内的缓存

fixture 默认作用域是 `function`。在同一个测试中，一个 fixture 即使通过多条依赖路径
被请求，也只执行一次。因此：

```text
test 直接收到的 memory_sink
is
AuditService 内部持有的 memory_sink
```

下一个测试会重新创建 function-scoped fixture，所以可变状态不会自动泄漏到其他测试。

### fixture 的作用域

```python
@pytest.fixture(scope="module")
def expensive_resource():
    ...
```

常见作用域从短到长为：

```text
function → class → module → package → session
```

作用域越长，建立次数越少，但共享状态和测试耦合的风险越高。不要仅仅为了“更快”就把
可变数据库、列表或 fake 提升为 session scope。

### 使用 yield 清理资源

fixture 在 `yield` 前建立资源，在 `yield` 后清理：

```python
@pytest.fixture
def resource():
    value = open_resource()
    try:
        yield value
    finally:
        value.close()
```

即使测试抛出异常，清理部分也会运行。它适合文件、数据库连接、客户端和后台任务。

## 5. 确定性边界：为什么要注入 Clock

下面的代码很难稳定测试：

```python
def record(action: str) -> AuditRecord:
    return AuditRecord(action, datetime.now(UTC))
```

测试无法提前知道精确时间，只能使用范围或 patch 模块内部名称。更清楚的设计是把程序
真正需要的能力定义成小接口：

```python
class Clock(Protocol):
    def now(self) -> datetime: ...
```

生产环境使用：

```python
SystemClock()
```

测试使用：

```python
FrozenClock(fixed_now)
```

好处不只是“更容易测试”：

- 业务代码明确表达自己依赖时间。
- 测试不依赖运行速度和当前日期。
- 不需要知道 `datetime` 被导入到哪个模块名称下。
- 替身只实现 `now()`，不会伪造整个 datetime 模块。

同样思想适用于 ID、随机数、文件系统、HTTP 客户端和数据库。

## 6. 测试替身：fake、stub 与 mock

“测试替身”是总称，不同替身解决的问题不同。

| 类型 | 作用 | 例子 |
|---|---|---|
| dummy | 只为满足参数，不参与行为 | 不会被使用的 logger |
| stub | 为特定调用返回预设结果 | 总是返回固定时间的 Clock |
| fake | 有简化但真实可用的实现 | 用 list 保存记录的 MemoryAuditSink |
| spy | 记录真实调用，供测试事后查询 | 包装真实实现并保存调用历史 |
| mock | 预先关注交互，并提供调用断言 | `Mock(spec=AuditSink)` |

实际交流中这些词有时会混用，重要的是说清楚测试观察的是什么。

### 本章的 fake

```python
class MemoryAuditSink:
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def save(self, record: AuditRecord) -> None:
        self.records.append(record)
```

它实现了真实的保存行为，只是存储位置是内存。测试查询：

```python
assert sink.records == [record]
```

这验证最终状态，对内部调用次数不敏感。

### 带 spec 的 mock

```python
sink = Mock(spec=AuditSink)
```

`spec` 让 mock 只暴露 `AuditSink` 已声明的属性。例如拼错 `sink.store(...)` 会尽早失败。
然后可以验证：

```python
sink.save.assert_called_once_with(record)
```

但 `spec` 不是完整运行时类型检查器，也不会自动验证每个实参的静态类型。mock 还容易
把测试绑在当前调用步骤上，所以不要用它替代所有 fake。

## 7. 参数化：一条规则的输入矩阵

多个输入遵守同一条规则时，不必复制整个测试：

```python
@pytest.mark.parametrize(
    "action",
    ["", "   ", "\n\t"],
    ids=["empty", "spaces", "newline"],
)
def test_rejects_blank_actions(audit_service, action):
    ...
```

pytest 会把它展开为三个独立测试项。任何一个失败时，报告会显示对应 ID。

适合参数化的情况：

- 同一规则的边界值。
- 输入与期望结果的表格。
- 相同仓库契约运行在不同实现上。

不适合的情况：

- 每个输入需要完全不同的准备和断言。
- 为减少测试数量，把无关业务场景塞进一个巨大参数表。

异常测试应尽量同时验证异常类型和稳定的业务信息：

```python
with pytest.raises(ValueError, match="不能为空"):
    ...
```

不要依赖第三方库可能随版本变化的完整英文错误文本。

## 8. pytest 内置边界 fixture

### tmp_path

`tmp_path` 为每个测试提供独立临时目录，类型是 `pathlib.Path`：

```python
def test_export(tmp_path: Path) -> None:
    output = tmp_path / "audit.jsonl"
    ...
```

它避免：

- 写死 `/tmp/example.txt`。
- 污染仓库目录。
- 并行测试争用同一个文件。
- 上次运行残留文件让本次测试误通过。

验证 JSONL 时，应解析内容并比较字段，而不是比较容易受空格、字段顺序影响的整段文本。

### monkeypatch

`monkeypatch` 临时改变进程边界，并在测试结束后自动恢复：

```python
monkeypatch.setenv("AUDIT_CHANNEL", "ci")
```

还可以临时修改属性、字典项和当前目录。只 patch 代码实际查询的边界；如果业务对象可以
直接注入，就优先注入，不要 patch 深层实现。

### caplog

`caplog` 捕获 `logging` 记录：

```python
caplog.set_level(logging.INFO)
```

本章的服务记录：

```python
logger.info("audit_recorded", extra={"action": record.action})
```

测试应验证稳定的事件名和结构化字段，不断言完整时间戳或 formatter 生成的整行文本。
格式属于入口层配置，业务事件才是本测试关心的契约。

## 9. 异步测试：用事件协调，不猜时间

项目配置了 pytest-asyncio，因此 `async def test_*` 可以直接由 pytest 运行：

```python
async def test_something() -> None:
    result = await operation()
    assert result == expected
```

并发测试最常见的错误是使用较长 `sleep()` 猜测任务已经运行：

```python
await asyncio.sleep(0.1)
```

机器忙、CI 调度变化或实现变快后，这种测试可能偶发失败。应使用 `asyncio.Event` 表达
真正的先后关系：

```text
worker 设置 started
test 等待 started
test 取消外层任务
worker 的 finally 设置 cleanup_finished
test 验证取消继续传播且 cleanup_finished 已设置
```

短 timeout 可以作为“测试卡死时尽快失败”的保护，但不应该代替事件同步。

### 取消不是普通失败

测试取消时应该验证两个独立契约：

1. 外层等待得到 `asyncio.CancelledError`。
2. worker 的 `finally` 已完成清理。

如果只验证第一项，后台资源仍可能泄漏；如果把取消转换成普通结果，调用方又无法知道
操作被中止。

## 10. 单元测试、集成测试和端到端测试

测试层级取决于穿过了多少真实边界：

```text
单元测试
→ 一个小行为，依赖使用内存实现或可控替身

集成测试
→ 多个真实组件协作，例如真实 sqlite3 SQL + 文件型临时数据库

端到端测试
→ 从公开入口穿过完整系统，例如安装后的 CLI 或真实 HTTP server
```

不是“一个测试只能调用一个函数”才算单元测试，也不是使用 mock 就自动成为单元测试。
本章大部分练习是单元测试；第 18 章会使用 `tmp_path` 测试真实 SQLite 文件；第 16 章
的 wheel smoke test 属于更高层验收。

低层测试通常更快、定位更精确；高层测试覆盖真实组装，但建立成本更高。项目需要组合，
而不是只追求某一层。

## 11. 覆盖率能告诉你什么

覆盖率可以发现从未执行的分支，例如：

```text
错误分支没有测试
清理路径从未执行
某个状态转换完全遗漏
```

它不能证明：

- 断言写对了。
- 业务需求完整。
- 并发不存在竞态。
- 100% 覆盖的代码一定可靠。

先根据规则设计测试，再用覆盖率寻找遗漏；不要为了数字执行代码却不验证行为。

## 12. 本章练习顺序

不要一次填完全部 TODO。按下面顺序学习：

### 12.1 fixture 与 fake

完成：

```text
fixed_now
memory_sink
audit_service
test_service_records_normalized_action_in_fake
```

只运行：

```bash
uv run pytest \
  lessons/15_testing/test_lesson.py::test_service_records_normalized_action_in_fake -q
```

重点解释同一个 `memory_sink` 为什么同时出现在服务内部和测试参数中。

### 12.2 参数化与异常

完成空 action 参数化测试：

```bash
uv run pytest lessons/15_testing/test_lesson.py -k blank -q
```

重点区分“一条规则的多个输入”与“多个无关业务场景”。

### 12.3 tmp_path、monkeypatch 与 caplog

逐项完成文件、环境和日志测试：

```bash
uv run pytest lessons/15_testing/test_lesson.py -k "temporary or environment or log" -q
```

重点识别每个 fixture 隔离的是哪个外部边界。

### 12.4 mock 交互

完成带 `spec` 的 sink mock 测试：

```bash
uv run pytest lessons/15_testing/test_lesson.py -k spec_mock -q
```

重点说明为什么这里只验证 `save(record)`，而前面的 fake 测试验证 `records` 状态。

### 12.5 异步取消

最后完成取消与清理：

```bash
uv run pytest lessons/15_testing/test_lesson.py -k cancelling -q
```

全部通过后运行：

```bash
uv run pytest lessons/15_testing/test_lesson.py -q
```

然后才查看参考测试。

## 13. 调试 pytest 的常用命令

```bash
# 第一项失败后停止
uv run pytest path/to/test.py -x

# 只运行名称匹配的测试
uv run pytest path/to/test.py -k keyword

# 精确运行一个测试
uv run pytest path/to/test.py::test_name

# 展示更详细的测试名称
uv run pytest path/to/test.py -vv

# 展示 fixture 建立与清理顺序
uv run pytest path/to/test.py --setup-show

# 列出可用 fixture
uv run pytest --fixtures path/to/test.py

# 不捕获 stdout/stderr，适合临时诊断
uv run pytest path/to/test.py -s
```

`-s` 和临时 `print()` 适合诊断，但最终测试应依靠清楚的断言表达需求。

## 14. 常见错误

### fixture 承担太多职责

一个 fixture 同时创建数据、打开数据库、修改环境、启动线程并写日志，会让依赖关系难以
理解。优先拆成可以组合的小 fixture。

### 测试依赖执行顺序

不要让 `test_b` 依赖 `test_a` 留下的数据。每个测试都应独立建立前提。

### patch 错名称

Python patch 的是被测试模块实际查询的名称，不一定是对象最初定义的位置。更好的选择
往往是把小接口作为参数注入。

### 过度验证实现步骤

如果返回值和最终状态已经能表达规则，就不必再断言每个内部函数的调用顺序。

### 使用真实时间和长 sleep

固定时钟、Event、fake transport 和临时目录通常能提供更快、更稳定的测试。

### 测试只执行代码而没有有效断言

“没有抛异常”有时是契约，但大多数测试还应验证真正的输出、状态或交互。

## 15. 完成标准与复习题

完成本章时，应满足：

- 练习中的九个测试全部通过。
- 能画出 fixture 依赖图并说明同一测试内的缓存。
- 能解释 fake 与 mock 分别观察状态还是交互。
- 文件、环境、日志和时间测试都不依赖开发机状态。
- 取消测试不使用长时间 sleep，并验证 `finally` 清理。
- 能说明覆盖率为什么不能代替业务断言。

复习题：

1. pytest 为什么知道测试函数参数 `memory_sink` 应该从哪里获得？
2. 测试直接请求的 `memory_sink` 为什么与 `AuditService` 内部的是同一个对象？
3. function scope 与 session scope 对可变 fake 有什么影响？
4. `yield` fixture 在测试抛异常后为什么仍能清理？
5. `FrozenClock` 为什么通常优于 patch 整个 `datetime` 模块？
6. fake 与 mock 分别更适合验证什么？
7. `Mock(spec=AuditSink)` 能防止什么，不能保证什么？
8. 为什么异步测试更适合使用 `Event` 而不是较长 `sleep()`？
9. 覆盖率达到 100% 为什么仍不能证明程序正确？
