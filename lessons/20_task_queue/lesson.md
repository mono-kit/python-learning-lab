<!-- course-chapter: 20 -->

# 第 20 章：本地任务队列综合项目

这一章把领域模型、Protocol、应用服务、SQLite、Pydantic、asyncio、日志、CLI 和打包
连成一个可安装程序。它不再提供一个待补全的小函数，而是要求你按可执行里程碑逐层建立
系统；每一关只引入一个新的工程边界。

## 1. 目标架构

```text
CLI / 输入模型
      ↓
TaskService（用例编排）
      ↓
Task（领域状态机） ← Repository / Handler Protocol
      ↑                         ↑
SQLite adapter          asyncio executor
```

依赖始终指向领域和端口。CLI 不直接拼 SQL，执行器不自行修改任务字段，Pydantic 只处理
输入输出，SQLite 只负责持久化映射。

## 2. 学习方法

先阅读 [`exercise.md`](exercise.md) 的用户故事，再按 `tests/` 中编号逐关运行。不要一开始
运行全部未完成测试；当前一关通过后再进入下一关。综合项目故意没有完整参考答案，因为
模块切分、组合根和错误信息也是需要你自己做出的工程决策。

```bash
uv run pytest lessons/20_task_queue/tests/test_01_domain.py
uv run pytest lessons/20_task_queue/tests/test_02_service.py
```

## 3. 完成标准

- 状态变化只能通过领域方法发生，非法变化有明确异常；
- 服务可替换内存与 SQLite 仓库；
- 多项任务并发执行时有上限、超时、清理和失败隔离；
- CLI 具有稳定的命令接口；
- wheel 安装到源码目录外后仍能运行；
- 每个里程碑都有测试，日志不包含敏感数据。
