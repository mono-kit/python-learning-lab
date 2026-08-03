# Python 深入与工程实践路线

## 课程定位

这一阶段的目标不是继续收集零散语法，而是建立两种能力：

1. 能从 Python 数据模型、协议和运行时机制解释代码为什么这样工作。
2. 能把一组函数和类组织成可测试、可维护、可发布的小型工程。

学习完成后，应能独立完成一个带命令行、配置、持久化、并发处理、日志和
完整测试的 Python 应用。

## 学习方式

每章固定采用同一循环：

```text
预测行为
→ 运行最小示例
→ 解释底层协议
→ 完成练习
→ 编写边界测试
→ 重构并记录结论
```

每章应包含四类文件：

```text
src/python_learning_lab/advanced/     可运行讲解代码
src/python_learning_lab/engineering/  工程化示例
exercises/                             TODO 练习
tests/                                 可执行需求
```

不要先看参考答案。测试通过后，还要能够口头解释实现，而不只是得到绿色结果。

## 课程地图

| 顺序 | 主题 | 核心产出 |
|---|---|---|
| 10 | Python 数据模型 | 可比较、可哈希、可打印的值对象 |
| 11 | 属性协议、描述器与 MRO | 理解 property、方法绑定和多重继承 |
| 12 | 高级类型标注 | 泛型容器、Protocol 边界和类型收窄 |
| 13 | 流式处理与资源管理 | 惰性数据管道和可靠资源清理 |
| 14 | 深入 asyncio 与并发边界 | 可取消、限流、带超时的并发任务 |
| 15 | 深入 pytest | fixtures、替身、参数化和测试分层 |
| 16 | 模块、打包、发布与工具生态 | 可安装、可构建、可验证、可发布的 Python 包 |
| 17 | 应用架构与可观测性 | 分层服务、依赖倒置、配置和日志 |
| 18 | SQLite 与事务 | 可替换的持久化层和集成测试 |
| 19 | 性能与诊断 | 用测量结果定位 CPU、内存和 I/O 问题 |
| 20 | 综合项目：本地任务队列 | 串联全部语言和工程知识 |

## 10. Python 数据模型

建议文件：`src/python_learning_lab/advanced/data_model.py`

### 核心问题

- `repr()`、`str()` 和格式化协议有什么区别？
- `==` 如何调用 `__eq__`，`NotImplemented` 有什么作用？
- 为什么实现 `__eq__` 后需要重新考虑 `__hash__`？
- 可变对象为什么通常不适合作为字典键？
- `len()`、`in`、索引和迭代分别调用什么协议？

### 示例内容

实现不可变值对象 `Money`：

```python
@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str
```

逐步加入：

- 可读的 `repr`
- 同币种加法
- 相等与哈希
- 排序规则
- 自定义格式化

再实现一个只读 `Inventory` 容器，支持：

```python
len(inventory)
product_id in inventory
inventory[product_id]
for item in inventory
```

### 练习

实现 `Version` 值对象，支持解析 `"2.10.3"`、比较、哈希和格式化。

### 完成标准

- 能说明运算符只是特殊方法的语法糖。
- 能解释相等对象为什么必须具有相同哈希值。
- 测试集合去重、字典键、非法运算和 `NotImplemented` 分支。

## 11. 属性协议、描述器与 MRO

建议文件：`src/python_learning_lab/advanced/object_protocols.py`

### 核心问题

- `obj.name` 的属性查找顺序是什么？
- 实例方法为什么会自动绑定 `self`？
- `property` 本质上为什么是描述器？
- `__getattr__` 与 `__getattribute__` 有什么区别？
- `super()` 是怎样沿 MRO 查找的？

### 示例内容

从最小描述器开始：

```python
class PositiveNumber:
    def __set_name__(self, owner, name): ...
    def __get__(self, instance, owner): ...
    def __set__(self, instance, value): ...
```

用它为多个类复用正数校验，并与 `property`、实例 `__dict__`、
`slots=True` 对照。

多重继承部分实现可协作的 mixin，观察：

```python
ClassName.__mro__
super().method()
```

### 练习

实现 `NonEmptyString` 和 `BoundedInteger` 描述器，再组合成 `Account`。

### 完成标准

- 能画出一次属性读取和赋值的查找流程。
- 能解释数据描述器为什么优先于实例字典。
- 多重继承链中每个实现只执行一次。

## 12. 高级类型标注

建议文件：`src/python_learning_lab/advanced/typing_lab.py`

### 核心问题

- `Any`、`object` 和泛型类型参数有什么区别？
- `TypeVar` 如何保留输入与输出之间的类型关系？
- `Protocol` 与抽象基类分别适合什么边界？
- `TypedDict`、Pydantic 模型和 dataclass 应怎样选择？
- 类型收窄如何减少不安全的断言和强制转换？

### 示例内容

实现泛型仓库接口：

```python
T = TypeVar("T")
ID = TypeVar("ID", bound=Hashable)

class Repository(Protocol[ID, T]):
    def get(self, item_id: ID) -> T | None: ...
    def save(self, item: T) -> None: ...
```

课程覆盖：

- `TypeVar`、`Generic` 和有界类型变量
- `Protocol` 与结构化子类型
- `Literal`、`TypedDict`、`TypeGuard` 和 `overload`
- `Self` 与协变、逆变的直觉
- `ParamSpec` 保留装饰器函数签名

### 练习

实现类型安全的内存缓存 `Cache[K, V]`，并为装饰器保留参数与返回类型。

### 完成标准

- 运行时测试通过。
- 静态类型检查无错误。
- 公共接口不使用无理由的 `Any`。

## 13. 流式处理与资源管理

建议文件：`src/python_learning_lab/advanced/streaming.py`

### 核心问题

- 什么时候返回列表，什么时候返回迭代器？
- 生成器的 `send()`、`throw()`、`close()` 分别做什么？
- 怎样构建不会一次加载全部数据的处理管道？
- 多个资源如何保证按相反顺序释放？

### 示例内容

构建 JSON Lines 数据管道：

```text
逐行读取
→ 解析 JSON
→ Pydantic 校验
→ 过滤无效记录
→ 分批输出统计
```

课程覆盖：

- `Iterator` 与单次消费语义
- 生成器清理和 `GeneratorExit`
- `contextmanager` 与类式上下文管理器
- `ExitStack` 管理动态数量的资源
- `itertools` 组合惰性步骤

### 练习

实现 `validated_batches(path, batch_size)`，保证大文件流式读取、错误带行号、
文件始终关闭，并且不会多消费迭代器。

### 完成标准

- 测试空文件、损坏行、提前停止和异常清理。
- 能用内存占用解释为什么该实现适合大文件。

## 14. 深入 asyncio 与并发边界

建议文件：`src/python_learning_lab/advanced/concurrency.py`

### 核心问题

- 取消是如何在 `await` 处传播的？
- `TaskGroup` 中一个任务失败时，其他任务会怎样？
- 怎样限制并发量并形成背压？
- 线程、进程和协程各适合哪类工作？
- GIL 对 CPU 密集任务意味着什么？

### 示例内容

实现并发抓取模拟器：

```python
asyncio.timeout(...)
asyncio.Semaphore(...)
asyncio.Queue(...)
asyncio.TaskGroup()
```

课程覆盖：

- 取消、超时和清理
- `ExceptionGroup` 与 `except*`
- Queue 生产者—消费者
- Semaphore 限流
- `asyncio.to_thread()` 隔离阻塞 I/O
- 进程池处理 CPU 密集任务的边界

### 练习

实现最多同时运行 3 项工作的任务执行器，支持超时、取消、失败收集和有序结果。

### 完成标准

- 测试并发上限，而不依赖不稳定的长时间 `sleep`。
- 任务失败后没有遗留后台任务。
- 能解释并发、并行和异步的区别。

## 15. 深入 pytest

建议文件：`src/python_learning_lab/engineering/testing_lab.py`

### 核心问题

- 单元测试、集成测试和端到端测试的边界在哪里？
- fixture 应该提供数据、资源还是行为？
- 什么时候使用 fake，什么时候使用 mock？
- 如何测试时间、随机数、网络失败和异步取消？

### 示例内容

课程覆盖：

- fixture 作用域与组合
- 参数化和自定义测试 ID
- `tmp_path`、`monkeypatch` 和 `caplog`
- `unittest.mock` 的 `spec` 与调用断言
- 异步测试和失败注入
- 覆盖率的含义与局限
- 可选：使用 Hypothesis 做性质测试

### 练习

为前面任务执行器建立测试矩阵：成功、超时、取消、部分失败、顺序和并发上限。

### 完成标准

- 测试不依赖真实网络、当前时间或执行顺序偶然性。
- 每个测试失败时能清楚指出一条业务规则。
- 覆盖率用于发现遗漏，而不是追求无意义的 100%。

## 16. 模块、打包、发布与工具生态

完整讲义：[`docs/packaging.md`](packaging.md)

这一章扩展为四个连续单元，而不是只学习一个构建命令。

### 16A. 模块与导入系统

- 模块对象、`__name__`、`__package__`、`__spec__`
- `sys.path` 查找与 `sys.modules` 缓存
- 常规包、namespace package 和 `__init__.py`
- 绝对导入、相对导入与 `python -m`
- 循环导入的诊断和职责重构
- `importlib.resources` 与 `importlib.metadata`
- 模块、import package、distribution package 和项目的区别

### 16B. 构建标准与产物

- `pyproject.toml` 的 `[build-system]`、`[project]` 和 `[tool.*]`
- 运行依赖、optional dependencies 和 dependency groups
- 构建前端与构建后端的职责
- 构建隔离与 editable install
- sdist、纯 Python wheel 和平台 wheel
- setuptools、Hatchling、flit-core、pdm-backend、uv-build
- Maturin 与 scikit-build-core 的原生扩展场景

### 16C. 版本、发包与验证

- PEP 440 版本与预发布版本
- 包名、元数据、许可证、README 和 CLI entry point
- 使用 `build`/`twine` 的标准流程
- 使用 `uv build`/`uv publish` 的现代流程
- 在全新环境验证 wheel 和从 sdist 重建
- TestPyPI 演练、正式 PyPI、token 与 Trusted Publishing
- 发布不可覆盖、yank 和新版本修复策略

### 16D. 工具生态与迁移

- venv + pip + build + twine：理解职责的标准基线
- uv：Python、环境、依赖、锁文件、运行、工具、构建和发布
- Nox：用隔离 session 编排多版本测试、检查、构建和产物验证
- Nox 使用 `uv|virtualenv` 后端：uv 管环境，Nox 管任务矩阵
- Rye：官方已停止开发，只作为迁移到 uv 的遗留案例
- Poetry、PDM、Hatch、pip-tools 和 pipx 的定位
- 比较“项目管理前端”和“构建后端”，避免按品牌混淆职责

### 练习

1. 观察模块第一次导入与缓存行为，修复一个循环导入。
2. 为项目增加 `python-learning-lab` CLI entry point 和包内资源。
3. 构建并审计 sdist/wheel，在干净虚拟环境运行 smoke test。
4. 用标准工具链和 uv 分别完成同一构建流程。
5. 在独立示例包比较 setuptools、Hatchling、flit-core 和 uv-build。
6. 在 TestPyPI 完成一次不会影响正式索引的发布演练。
7. 把给定 Rye 遗留项目迁移到 uv，并证明行为一致。
8. 用 Nox 建立 tests、lint、typing、build、package_smoke 和
   release_check sessions。

### 完成标准

- 不依赖修改 `PYTHONPATH` 运行项目。
- 能解释模块、导入包、分发包和项目的区别。
- 能解释安装器、解析器、构建前端、构建后端和上传工具的区别。
- 能独立配置元数据、依赖、入口点和构建系统。
- 能检查产物内容，并从项目目录外验证安装后的包。
- 能安全区分 TestPyPI 演练与正式发布。
- 新项目优先掌握 uv，同时能维护和迁移 Rye 项目。
- 能用 Nox 在隔离环境和多个 Python 版本中重复执行质量门禁。

## 17. 应用架构与可观测性

建议目录：`src/python_learning_lab/engineering/`

### 核心问题

- 领域规则、I/O 和框架代码为什么要分开？
- 如何通过 Protocol 做依赖倒置，而不是到处传递全局对象？
- 什么错误应该转换，什么错误应该继续传播？
- 日志与 `print()` 的职责有什么不同？

### 示例结构

```text
engineering/
├── domain.py       领域对象和规则
├── ports.py        Repository、Clock 等 Protocol
├── service.py      用例编排
├── adapters.py     文件或网络适配器
├── settings.py     配置边界
└── cli.py          用户入口
```

课程覆盖：

- 分层和依赖方向
- 领域异常与边界异常转换
- `logging` 的 logger、level、handler 和 formatter
- 结构化上下文和异常日志
- 可注入的时间、ID 生成器和存储接口

### 练习

把购物车逻辑重构为不依赖 Pydantic 的领域层，并让 Pydantic 只负责输入输出边界。

### 完成标准

- 领域层不读取环境变量、不访问磁盘、不打印日志到终端。
- 服务可以使用内存 fake 完成快速单元测试。
- CLI 和持久化层可以替换而不改领域规则。

## 18. SQLite 与事务

建议文件：`src/python_learning_lab/engineering/storage.py`

### 核心问题

- 事务的提交和回滚解决什么问题？
- SQL 参数绑定为什么不能用字符串拼接替代？
- 数据库行如何转换成领域对象？
- 怎样让测试既快又能覆盖真实 SQL？

### 示例内容

- `sqlite3` 连接和上下文管理
- 参数化 SQL
- 表结构初始化和简单迁移
- 唯一约束与领域异常转换
- `Repository` Protocol 的 SQLite 实现
- 使用临时数据库做集成测试

### 练习

实现任务仓库的新增、查询、状态更新和事务回滚。

### 完成标准

- 所有 SQL 使用参数绑定。
- 失败事务不会留下部分写入。
- 同一套服务测试可以运行在内存仓库和 SQLite 仓库上。

## 19. 性能与诊断

建议文件：`src/python_learning_lab/advanced/performance.py`

### 核心问题

- 如何区分算法问题、CPU 问题、I/O 等待和内存问题？
- 为什么没有测量就不应该先优化？
- 生成器一定比列表快吗？
- 缓存在哪些情况下会让程序更慢或占用更多内存？

### 示例内容

- 用 `timeit` 比较小片段
- 用 `cProfile` 和 `pstats` 找热点
- 用 `tracemalloc` 比较内存分配
- 比较列表、生成器、集合查找和不同算法复杂度
- 检查 `lru_cache` 的命中率和缓存增长

### 练习

为大文件统计程序建立基准，先定位瓶颈，再提交有数据支持的优化。

### 完成标准

- 优化前后都有可重复的测量。
- 能说明时间、内存和代码复杂度之间的取舍。
- 不为不可测量的微小收益牺牲可读性。

## 20. 综合项目：本地任务队列

建议目录：`src/python_learning_lab/task_queue/`

### 用户功能

```text
添加任务
列出任务
并发执行待处理任务
查看成功或失败原因
重试失败任务
取消等待中的任务
```

### 技术要求

- 使用 Pydantic 处理 CLI 输入、配置和公开输出。
- 使用 dataclass 表达不依赖框架的领域对象。
- 使用 Protocol 定义仓库、时钟和任务处理器接口。
- 使用 SQLite 持久化任务和状态变化。
- 使用 `asyncio.Queue` 与 `TaskGroup` 执行任务。
- 支持并发上限、超时、取消和失败隔离。
- 使用 `logging` 输出可诊断信息。
- 使用 pytest 编写单元测试和 SQLite 集成测试。
- 通过模块入口或安装后的命令启动。

### 建议状态机

```text
PENDING → RUNNING → SUCCEEDED
                  ↘ FAILED → PENDING（重试）

PENDING → CANCELLED
```

非法状态变化必须抛出明确的领域异常。

### 验收标准

1. `pytest` 全部通过，测试不依赖真实网络。
2. 静态类型检查和代码规范检查通过。
3. 新环境中可以构建、安装并运行命令行程序。
4. 中途失败不会破坏数据库状态或遗留异步任务。
5. README 能让另一位开发者在十分钟内运行项目。

## 推荐节奏

| 周次 | 内容 |
|---|---|
| 1 | 数据模型 |
| 2 | 描述器、属性协议和 MRO |
| 3 | 高级类型标注 |
| 4 | 流式处理和资源管理 |
| 5 | asyncio、取消、超时和限流 |
| 6 | pytest 深入 |
| 7 | 模块、导入系统和循环导入 |
| 8 | pyproject、构建前后端、sdist 和 wheel |
| 9 | uv、Nox、工具生态、TestPyPI 和发布演练 |
| 10 | 应用架构、日志和配置 |
| 11 | SQLite、事务和集成测试 |
| 12 | 性能诊断与综合项目设计 |
| 13～14 | 完成综合项目和复盘 |

每周建议安排三次学习：

```text
第一次：阅读、预测和运行示例
第二次：独立完成练习
第三次：补测试、重构和写复习笔记
```

## 工具引入顺序

先使用当前项目已有的 Python、Pydantic 和 pytest。进入工程阶段后再逐步加入：

1. venv、pip、build、twine：建立符合标准的打包发布基线。
2. uv：管理 Python、环境、依赖、锁文件、运行、构建和发布。
3. Nox：把测试、检查、构建和产物验证编排成隔离 session。
4. Rye 迁移练习：理解遗留工具配置，但不用于创建新项目。
5. Ruff：格式和代码规范。
6. 静态类型检查器：验证公共接口和泛型设计。
7. pytest-cov：发现没有被测试覆盖的分支。
8. Hypothesis（可选）：为值对象和数据转换做性质测试。

一次只引入一个工具，必须先能解释它解决的问题，再把它加入项目配置。

## 第一课

从“Python 数据模型”开始，不急着写描述器。第一课只实现 `Money` 的
表示、相等、哈希和加法，并用测试回答这个问题：

> 为什么两个相等的对象如果哈希不同，会破坏 set 和 dict 的行为？
