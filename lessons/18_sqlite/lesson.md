<!-- course-chapter: 18 -->

# 第 18 章：SQLite 与事务

这一章学习 Python 标准库 `sqlite3`，重点不是背 SQL，而是理解连接、参数绑定、领域对象
映射和事务所有权。完成后，你应能实现一个不会提前提交、失败时不会留下部分数据的
仓库适配器。

配套内容：

- 完整示例：`lessons/_shared/task_queue/storage.py`
- 练习：`lessons/18_sqlite/exercise.py`
- 验收：`lessons/18_sqlite/test_lesson.py`
- 参考答案：`lessons/18_sqlite/solution.py`

先运行：

```bash
uv run pytest lessons/18_sqlite/test_lesson.py -q
```

## 1. SQLite 与 Python DB-API

SQLite 是嵌入式数据库：数据库引擎运行在当前进程中，数据可以放在磁盘文件，也可以放在
内存。Python 的 `sqlite3` 实现了 DB-API 2.0 风格接口。

```python
import sqlite3

connection = sqlite3.connect(":memory:")
cursor = connection.execute("SELECT 1 AS value")
row = cursor.fetchone()
assert row[0] == 1
connection.close()
```

几个对象的职责：

- `Connection` 管理数据库会话和事务；
- `Cursor` 执行语句并遍历结果；
- `execute()` 是连接提供的便捷方法，会返回 cursor；
- `fetchone()`、`fetchall()` 取出结果行；
- `commit()` 和 `rollback()` 决定当前事务的结果。

连接是有状态资源，不应在模块导入时创建。创建它的入口也应该负责关闭它。

## 2. 表结构是持久化层的不变量

最小任务表可以这样初始化：

```python
connection.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        error TEXT
    )
    """
)
```

`PRIMARY KEY` 和 `NOT NULL` 是数据库边界的保护，不替代领域规则，却能防止其他写入路径
破坏数据。正式项目通常使用迁移工具维护版本；本课程先用幂等的 `initialize()` 理解基础。

`CREATE TABLE IF NOT EXISTS` 只保证表存在，不会自动把旧表改成新结构。真实演进需要有序、
可回滚或可恢复的迁移，而不是每次启动临时拼接 `ALTER TABLE`。

## 3. 参数绑定不是字符串格式化

永远把 SQL 结构和数据分开：

```python
row = connection.execute(
    "SELECT id, text FROM notes WHERE id = ?",
    (note_id,),
).fetchone()
```

问号是 SQLite 的参数占位符。第二个参数必须是序列；单元素元组要写成 `(note_id,)`，而
不是 `(note_id)`。驱动负责正确编码引号和特殊字符。

错误示例：

```python
# 不要这样做：数据会变成 SQL 语法的一部分。
sql = f"SELECT id, text FROM notes WHERE id = '{note_id}'"
```

参数绑定不仅防 SQL 注入，也正确处理引号、Unicode、空值和二进制数据。它只能绑定值，
不能绑定表名或列名；动态标识符需要白名单映射，而不是接受任意用户字符串。

## 4. row_factory 让行映射更清晰

默认结果行像 tuple，需要记住列位置。设置 `row_factory` 后可以按列名读取：

```python
connection.row_factory = sqlite3.Row
row = connection.execute(
    "SELECT id, title, status, error FROM tasks WHERE id = ?",
    (task_id,),
).fetchone()

if row is None:
    task = None
else:
    task = Task(
        id=str(row["id"]),
        title=str(row["title"]),
        status=TaskStatus(str(row["status"])),
        error=str(row["error"]) if row["error"] is not None else None,
    )
```

映射函数是适配器的一部分。数据库保存 `status.value` 字符串，领域层使用 `TaskStatus`；
SQLite 的 `NULL` 映射成 Python `None`。不要让 `sqlite3.Row` 穿过仓库边界进入领域服务。

## 5. UPSERT 表达“保存”的语义

仓库的 `save()` 在本项目中表示“同 ID 已存在就更新，否则新增”：

```python
connection.execute(
    """
    INSERT INTO notes (id, text) VALUES (?, ?)
    ON CONFLICT(id) DO UPDATE SET text = excluded.text
    """,
    (note.id, note.text),
)
```

这里的 `excluded.text` 是本次原本想插入的新值。是否应使用 UPSERT 是领域选择；如果系统
要求“重复创建必须报错”，就不应悄悄更新。先定义端口语义，再写对应 SQL。

## 6. 事务保证一组操作的原子性

假设一个用例连续保存两个对象，第二次失败。没有正确事务边界时，第一个对象可能已经
提交，系统进入“完成一半”的状态。事务要求：要么全部提交，要么全部回滚。

```python
@contextmanager
def transaction(self) -> Iterator[sqlite3.Connection]:
    if self.connection.in_transaction:
        raise RuntimeError("不支持嵌套事务")

    self.connection.execute("BEGIN")
    try:
        yield self.connection
    except BaseException:
        self.connection.rollback()
        raise
    else:
        self.connection.commit()
```

执行过程是：

1. `BEGIN` 明确开始事务；
2. `yield` 把控制权交给 `with` 块；
3. 正常退出执行 `commit()`；
4. 任何异常退出执行 `rollback()`，随后原异常继续传播。

这里捕获 `BaseException` 是为了取消、键盘中断等非 `Exception` 退出也能回滚；代码没有
吞掉异常。资源清理与错误处理是两个不同职责。

## 7. 谁拥有事务，谁决定提交

这是本章最容易出错的地方。单独调用 `save()` 时，它应该保证自己的写入提交；但如果
外层已经开启事务，`save()` 必须加入外层事务，不能擅自提交：

```python
def save(self, note: Note) -> None:
    if self.connection.in_transaction:
        self._save(note)
        return

    with self.connection:
        self._save(note)
```

如果 `save()` 每次都写成 `with self.connection:`，外层 `transaction()` 中第一次保存
退出内部 `with` 时就可能提交，之后的回滚无法撤销它。正确原则是：最外层用例拥有事务，
内部仓库操作不能越权结束它。

```python
with repository.transaction():
    repository.save(Note("a", "first"))
    repository.save(Note("b", "second"))
```

若第二次写入失败，`a` 和 `b` 都不应存在。验收测试会专门检查这一点。

## 8. Connection 上下文管理器容易被误解

`with sqlite3.connect(...) as connection:` 在正常退出时提交、异常退出时回滚，但通常
**不会替你关闭连接**。同样，`with connection:` 管理的是事务行为，不是连接生命周期。

如果需要保证关闭，可以显式使用 `try/finally`：

```python
connection = sqlite3.connect(path)
try:
    repository = SQLiteNoteRepository(connection)
    repository.initialize()
    repository.save(Note("note-1", "hello"))
finally:
    connection.close()
```

不要只凭“使用了 with”判断资源一定关闭，要查清对象的上下文协议究竟管理什么。

## 9. 嵌套事务与 savepoint

本课程实现检测 `connection.in_transaction` 并拒绝嵌套事务：

```python
if connection.in_transaction:
    raise RuntimeError("不支持嵌套事务")
```

这是一个明确、可预测的契约。SQLite 没有通过再次 `BEGIN` 自动创建真正的嵌套事务。
复杂项目可以用 `SAVEPOINT`、`ROLLBACK TO` 和 `RELEASE` 实现局部回滚，但必须明确设计
所有权和嵌套语义，不能简单套两层 `with connection:`。

## 10. 内存数据库和临时文件测试不同风险

内存数据库速度快、隔离好：

```python
@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")
    value = SQLiteNoteRepository(connection)
    value.initialize()
    try:
        yield value
    finally:
        connection.close()
```

但它不会验证关闭后重新打开仍可读取。持久化行为要用 `tmp_path`：

```python
def test_persists_after_reopen(tmp_path):
    path = tmp_path / "notes.sqlite3"
    first = sqlite3.connect(path)
    # 写入并关闭……
    first.close()

    second = sqlite3.connect(path)
    # 重新读取……
    second.close()
```

两类测试互补：内存库适合多数 SQL 行为，临时文件覆盖真实文件生命周期和提交问题。

## 11. 并发和连接边界

SQLite 很适合本地工具、单机服务和测试，但并发设计仍需谨慎：

- 默认连接有线程亲和限制，不要随意跨线程共享；
- 同一连接上同时执行多个操作会共享事务状态；
- SQLite 支持多个读取者，但写入最终需要序列化；
- 长事务会延长锁持有时间；
- 异步函数直接执行阻塞 SQL 仍会阻塞事件循环。

这不意味着必须立刻换数据库。先明确请求并发量、事务长度和持久化需求，再选择连接池、
线程边界或异步数据库库。

## 12. 本章练习顺序

在 `lessons/18_sqlite/exercise.py` 中依次完成：

1. `initialize()`：创建带主键和非空约束的 `notes` 表。
2. `get()`：使用参数绑定，存在时返回 `Note`，否则返回 `None`。
3. `_save()` 或等价内部逻辑：使用 UPSERT 保存和更新。
4. `save()`：独立调用时提交，已有事务时只写入。
5. `transaction()`：正常提交、异常回滚、拒绝嵌套。

每一步运行：

```bash
uv run pytest lessons/18_sqlite/test_lesson.py -q
```

再查看任务队列项目如何复用同一个 SQLite 适配器：

```bash
uv run pytest lessons/20_task_queue/tests/test_03_storage.py -q
```

验收不是只看 happy path。测试还会传入包含引号和 SQL 文本的普通数据、强制中途异常，
并关闭后重新打开磁盘数据库。

## 13. 常见误区

- 用 f-string 拼 SQL 数据；
- 把 `(note_id)` 误认为单元素 tuple；
- 在每个仓库方法里无条件提交，破坏外层原子性；
- 回滚后不重新抛出原异常；
- 把 `sqlite3.Row` 暴露给领域层；
- 只测 `:memory:`，没有覆盖文件持久化；
- 认为 `with connection:` 一定会关闭连接；
- 多个并发任务共享一个连接却没有设计所有权。

## 14. 完成标准与复习题

完成本章时，你应能：

- 解释 connection、cursor、row factory 和事务各自职责；
- 所有数据值均通过参数绑定进入 SQL；
- 映射数据库行与领域对象，而不泄漏驱动类型；
- 让一组仓库写入在异常时完整回滚；
- 区分事务生命周期和连接生命周期；
- 用内存数据库和 `tmp_path` 文件数据库覆盖不同风险。

请回答：

1. 为什么 `(note_id,)` 末尾必须有逗号？
2. 外层事务里调用两次 `save()` 时，谁有权执行 `commit()`？
3. 为什么参数绑定不能用于表名？动态表名应怎样处理？
4. `with connection:` 正常退出后，连接是否一定已经关闭？
5. 哪个测试能发现“写入没有真正提交到文件”的问题？
