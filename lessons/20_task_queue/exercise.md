<!-- exercise-chapter: 20 -->

# 第 20 章综合项目：本地任务队列

目标是把前面分散的语言与工程知识组装成一个可安装 CLI。不要复制讲解模块，
而是逐步建立自己的 `task_queue` 实现。

## 用户故事

```text
task-queue add "生成日报"
task-queue list
task-queue run --workers 3 --timeout 10
task-queue retry TASK_ID
task-queue cancel TASK_ID
```

## 领域规则

```text
PENDING → RUNNING → SUCCEEDED
                  ↘ FAILED → PENDING（retry）
PENDING → CANCELLED
```

非法变化抛出领域异常。失败任务必须保存原因；重试后清除旧错误。

## 里程碑

每一步的可执行契约位于 [`tests/`](tests/README.md)。
前四关验证已经具备的领域、服务、SQLite 与 Pydantic 基础；后两关驱动你实现执行器和
CLI。综合项目没有完整参考答案。

1. 用 dataclass 实现状态机及纯单元测试。
2. 定义 Repository、Clock、IdGenerator、TaskHandler Protocol。
3. 用内存 fake 实现 add、list、start、finish 用例。
4. 实现 SQLite 仓库，验证提交、回滚和参数绑定。
5. 用 Pydantic 建立 CLI 输入、配置和输出边界。
6. 使用 Queue、TaskGroup、Semaphore/worker 数量和 timeout 执行任务。
7. 加入日志上下文、失败隔离、重试与取消。
8. 声明 CLI entry point，构建 wheel，在项目目录外安装验证。
9. 用 Nox 编排测试、lint、typing、build 和 package_smoke。

从第一关开始运行：

```bash
uv run pytest lessons/20_task_queue/tests/test_01_domain.py
```

全部实现后再运行：

```bash
uv run pytest lessons/20_task_queue/tests
```

## 必测场景

- 空标题、重复 ID、找不到任务和所有非法状态变化。
- worker 成功、普通失败、超时、外层取消和并发上限。
- 一项失败不破坏其他任务结果，取消后没有遗留后台任务。
- SQLite 写入失败时没有半条状态更新。
- CLI 退出码、错误文本、包内资源以及安装后的命令。

## 验收

- `pytest`、Ruff 和静态类型检查通过。
- wheel 中不包含测试、缓存、数据库和开发机路径。
- 全新环境可以安装 wheel 并运行 CLI。
- README 能让另一位开发者十分钟内完成首次运行。
