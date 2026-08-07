# 第 20 章综合项目分阶段验收

这里的测试只描述最小行为契约，不提供任务队列实现或参考答案。请按顺序完成，
不要一开始运行全部文件；后面的失败信息就是下一阶段的实现提示。

## 学习顺序

| 里程碑 | 测试文件 | 当前基础 |
|---|---|---|
| 1. 领域状态机 | `test_01_domain.py` | 复用 `engineering.domain`，现在即可通过 |
| 2. 服务与可替换端口 | `test_02_service.py` | 复用 service 和内存适配器，现在即可通过 |
| 3. SQLite 持久化 | `test_03_storage.py` | 复用 SQLite 仓库，现在即可通过 |
| 4. Pydantic 边界 | `test_04_boundary_models.py` | 复用 `task_queue.models`，现在即可通过 |
| 5. 并发执行器 | `test_05_executor.py` | 需要自己新增实现 |
| 6. CLI | `test_06_cli.py` | 需要自己新增实现 |

逐关运行：

```bash
pytest lessons/20_task_queue/tests/test_01_domain.py
pytest lessons/20_task_queue/tests/test_02_service.py
pytest lessons/20_task_queue/tests/test_03_storage.py
pytest lessons/20_task_queue/tests/test_04_boundary_models.py
pytest lessons/20_task_queue/tests/test_05_executor.py
pytest lessons/20_task_queue/tests/test_06_cli.py
```

实现后也可以使用 `-x` 从第一项失败处继续：

```bash
pytest lessons/20_task_queue/tests -x
```

普通 `pytest` 的默认收集目录仍然是 `tests/`，因此尚未完成的综合项目不会干扰
仓库回归测试。

## 里程碑 5 的最小接口

新增模块：

```text
lessons._shared.task_queue.executor
```

模块至少公开 `TaskExecutor`，构造与调用契约为：

```text
TaskExecutor(service, handler, *, workers: int, timeout: float | None)
await executor.run_pending() -> Sequence[Task]
```

- `service` 是现有 `TaskService`。
- `handler` 是 `async handler(task: Task) -> None` 形式的异步可调用对象。
- `run_pending()` 只消费当前 `pending` 任务，并按输入顺序返回最终领域任务。
- 每项工作依次经过 `start` 和 `succeed`；普通异常与超时通过 `fail` 保存原因。
- 同时运行的 handler 不得超过 `workers`，一项失败不能取消其他项。

缺少模块或类时，测试会在测试函数内部给出上述契约，而不会在收集阶段抛出
`ImportError`。

## 里程碑 6 的最小接口

新增模块：

```text
lessons._shared.task_queue.cli
```

模块至少公开：

```text
build_parser() -> argparse.ArgumentParser
main(argv: Sequence[str] | None = None) -> int
```

parser 必须支持 `add`、`list`、`run`、`retry` 和 `cancel` 子命令，并把子命令名称
保存在 `args.command`：

- `add TITLE` → `args.title`
- `run --workers N --timeout SECONDS` → `args.workers`、`args.timeout`
- `retry TASK_ID`、`cancel TASK_ID` → `args.task_id`

`main(["--help"])` 可以返回 `0`，也可以遵循 argparse 约定抛出
`SystemExit(0)`；帮助文本必须列出五个子命令。
