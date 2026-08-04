# Python 深入与工程实践课程

这份文档是高级阶段的实际学习入口。路线为什么这样安排见
[`advanced-roadmap.md`](advanced-roadmap.md)，本文件回答每一章具体应该读什么、
运行什么、写什么和怎样验收。已经学完部分的复习记录见
[`advanced-review.md`](advanced-review.md)。

## 如何使用

每一章都按以下顺序进行：

1. 先阅读章节讲解和对应 `src` 示例，但暂时不运行。
2. 写下你预测的输出、调用的协议和可能出现的异常。
3. 使用 `python -m ...` 运行示例并解释差异。
4. 独立完成 `exercises/advanced/` 中对应题目。
5. 只运行这一章的 `learning_tests`，不要一次运行所有未完成练习。
6. 测试通过后再看 `solutions/advanced/`，比较职责、边界和类型设计。
7. 把本章最后的复习问题写进自己的 review 笔记。

普通回归测试不会收集 `learning_tests/`，所以后续章节的 TODO 不会干扰当前学习。

## 第 10 章：数据模型

讲解代码：`src/python_learning_lab/advanced/data_model.py`

```bash
python -m python_learning_lab.advanced.data_model
pytest learning_tests/test_10_data_model.py
```

学习重点：

- `+`、`<`、`len()`、`in` 和索引如何委托给特殊方法。
- `NotImplemented` 是让 Python 尝试反向运算或最终报错，不是抛出的异常。
- 相等对象必须具有相同哈希；可变值通常不适合作为字典键。
- `Mapping` 等抽象基类如何用少数核心方法补齐其余行为。

练习：实现可解析、可比较、可哈希的 `Version`。

复习问题：为什么 `Money + 1` 应返回 `NotImplemented`，而不同币种的两个
`Money` 应抛出业务异常？

## 第 11 章：属性协议、描述器与 MRO

讲解代码：`src/python_learning_lab/advanced/object_protocols.py`

```bash
python -m python_learning_lab.advanced.object_protocols
pytest learning_tests/test_11_descriptors.py
```

学习重点：

- 数据描述器、实例 `__dict__`、非数据描述器和 `__getattr__` 的查找优先级。
- `property`、函数和实例方法为什么都与描述器协议有关。
- `__set_name__` 如何让一个描述器知道自己绑定的属性名。
- `super()` 表示“从 MRO 中当前类的下一项继续”，不是“调用固定父类”。

练习：实现 `NonEmptyString` 与 `BoundedInteger`，组合成 `Account`。

复习问题：手动写入 `account.__dict__["age"]` 为什么不能遮蔽数据描述器？

## 第 12 章：高级类型标注

讲解代码：`src/python_learning_lab/advanced/typing_lab.py`

```bash
python -m python_learning_lab.advanced.typing_lab
pytest learning_tests/test_12_typing.py
```

学习重点：

- `object` 只允许安全的通用操作；`Any` 会关闭局部类型检查。
- 泛型参数保存输入、存储与输出之间的关系。
- `Protocol` 描述调用方需要的能力，不要求实现方显式继承。
- `TypeGuard` 收窄分支类型，`ParamSpec` 保留装饰器的参数签名。

练习：实现 `Cache[K, V]` 和不破坏签名的 `traced` 装饰器。

复习问题：为什么 `dict[Any, Any]` 虽然容易通过检查，却没有表达缓存的契约？

## 第 13 章：流式处理与资源管理

讲解代码：`src/python_learning_lab/advanced/streaming.py`

```bash
pytest learning_tests/test_13_streaming.py
```

学习重点：

- 生成器只在消费时运行，参数校验放在生成器体内也会被推迟。
- `with` 位于生成器中时，正常耗尽、异常和显式 `close()` 都会触发清理。
- `ExitStack` 管理运行时才知道数量的资源，并按进入的相反顺序退出。
- 流式管道控制内存峰值，但迭代器通常只能消费一次。

练习：逐行验证 JSONL，按批次产出模型，并在错误中保存行号。

复习问题：为什么返回 `Iterator[list[Event]]` 不等于“一次把所有批次装入列表”？

## 第 14 章：深入 asyncio

讲解代码：`src/python_learning_lab/advanced/concurrency.py`

```bash
python -m python_learning_lab.advanced.concurrency
pytest learning_tests/test_14_concurrency.py
```

学习重点：

- 取消会在协程下一个可取消的 `await` 处注入 `CancelledError`。
- `TaskGroup` 让子任务的生命周期不能悄悄逃出作用域。
- Semaphore 限制同时执行量；Queue 的有界容量还能对生产者形成背压。
- 超时是取消的一种结构化使用，清理代码仍应放在 `finally` 中。

练习：实现保持输入顺序、限制并发并区分成功/超时/失败的执行器。

复习问题：为什么不应写 `except BaseException` 并把取消当普通失败吞掉？

## 第 15 章：深入 pytest

讲解代码：`src/python_learning_lab/engineering/testing_lab.py`

本章不新增业务实现，而是为第 14、17、18 章补测试：

- fixture 负责资源建立与清理，测试函数描述一条业务规则。
- `tmp_path` 用于文件和 SQLite 集成测试。
- `monkeypatch` 改变进程边界；`caplog` 检查日志事件。
- fake 保存可查询状态；mock 更适合验证边界交互。
- 参数化覆盖规则矩阵，不把多个无关断言塞进一个测试。

复习问题：如果可以注入 `FrozenClock`，为什么通常不必 mock `datetime` 整个模块？

## 第 16 章：模块、打包、发布与工具

完整讲义：[`packaging.md`](packaging.md)

```bash
python -m python_learning_lab.advanced.imports_lab
uv run python -m python_learning_lab
uv build
uvx nox --list
```

实践顺序：

1. 观察 `__name__`、`__package__`、`__spec__` 和 `sys.modules`。
2. 从包内读取 `resources/welcome.txt`，并确认文件进入 wheel。
3. 使用项目声明的 CLI entry point，而不是依赖源码目录。
4. 分别用 `python -m build` 与 `uv build` 理解构建前端。
5. 用 Nox 编排测试、检查、构建和 wheel smoke test。
6. 阅读 `examples/rye_migration/`，把 Rye 当成遗留迁移案例。

复习问题：`uv build`、setuptools 和 `uv publish` 分别承担什么职责？

## 第 17 章：架构与可观测性

讲解代码：`src/python_learning_lab/engineering/`

阅读顺序：

```text
domain.py → ports.py → service.py → adapters.py
```

领域层只表达任务状态机；服务层依赖 Protocol；内存仓库和日志属于边界实现。
测试应能用同一套 `TaskService` 用例替换不同仓库。

复习问题：为什么 Pydantic 输入模型不应成为整个领域层唯一的数据模型？

练习与测试：

```bash
pytest learning_tests/test_17_architecture.py
```

## 第 18 章：SQLite 与事务

讲解代码：`src/python_learning_lab/engineering/storage.py`

```bash
pytest tests/test_engineering_lessons.py -k sqlite
```

学习重点：

- SQL 值使用参数绑定，表名等结构不能由不可信字符串拼接。
- connection 上下文在正常退出时提交、异常退出时回滚。
- 数据库行在适配器中转换为领域对象。
- `:memory:` 很快，但文件型临时数据库更接近真实连接生命周期。

复习问题：为什么事务失败后不能留下“状态已更新但错误信息未写入”的半成品？

练习与测试：

```bash
pytest learning_tests/test_18_storage.py
```

## 第 19 章：性能与诊断

讲解代码：`src/python_learning_lab/advanced/performance.py`

```bash
python -m python_learning_lab.advanced.performance
```

先用 `timeit` 比较稳定的小操作，再用 `cProfile` 找累计时间热点，用
`tracemalloc` 定位 Python 内存分配。优化报告必须保存输入规模、环境、测量方法、
修改前后结果和可读性取舍。

实验记录模板：`exercises/advanced/19_performance.md`

复习问题：生成器降低峰值内存，为什么不代表它在每个场景都比列表更快？

## 第 20 章：本地任务队列综合项目

项目任务书：`exercises/capstone/README.md`

综合项目不提供一份可以照抄的完整答案。前面章节已经提供各个零件，本章要求自己
完成 CLI、SQLite 仓库、并发执行器、状态机、配置、日志、测试与打包组装。

每完成一个纵向功能就运行测试，例如先实现“添加并列出”，再实现“执行成功”，
随后加入失败、重试、取消和超时。不要先建立所有目录再一次性填满。

## 工程命令速查

```bash
# 当前项目环境与测试
uv sync --extra dev
uv run pytest

# 单章练习
uv run pytest learning_tests/test_10_data_model.py

# 包入口和资源
uv run python-learning-lab
uv run python -m python_learning_lab.advanced.imports_lab

# 构建
uv build

# Nox 会话
uvx nox --list
uvx nox -s tests-3.11
uvx nox -s exercise -- learning_tests/test_10_data_model.py
uvx nox -s build package_smoke
```
