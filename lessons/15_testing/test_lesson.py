"""第 15 章练习：测试代码就是本章需要完成的产物。

运行：``pytest lessons/15_testing/test_lesson.py``

不要修改 ``testing_lab.py`` 或 ``concurrency.py`` 来迎合测试。逐个完成下面的 TODO，
让每个测试只描述一条规则，并保证测试不依赖真实时间、固定磁盘路径或长时间 sleep。
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from lessons._loader import load_file

concurrency = load_file("lessons/14_concurrency/exercise.py")
testing_lab = load_file("lessons/15_testing/example.py")
run_limited = concurrency["run_limited"]
AuditService = testing_lab["AuditService"]
AuditSink = testing_lab["AuditSink"]
FrozenClock = testing_lab["FrozenClock"]
MemoryAuditSink = testing_lab["MemoryAuditSink"]
audit_channel = testing_lab["audit_channel"]
export_records = testing_lab["export_records"]


@pytest.fixture
def fixed_now() -> datetime:
    # TODO: 返回一个带 UTC 时区的固定 datetime。
    raise NotImplementedError


@pytest.fixture
def memory_sink() -> MemoryAuditSink:
    # TODO: 返回保存可查询状态的 fake。
    raise NotImplementedError


@pytest.fixture
def audit_service(fixed_now: datetime, memory_sink: MemoryAuditSink) -> AuditService:
    # TODO: 组合 FrozenClock、MemoryAuditSink 和 AuditService。
    _ = FrozenClock
    raise NotImplementedError


def test_service_records_normalized_action_in_fake(
    audit_service: AuditService,
    memory_sink: MemoryAuditSink,
    fixed_now: datetime,
) -> None:
    # TODO: 验证返回值、去除首尾空白、固定时间以及 fake 中保存的状态。
    raise NotImplementedError


@pytest.mark.parametrize("action", ["", "   ", "\n\t"], ids=["empty", "spaces", "newline"])
def test_service_rejects_blank_actions(audit_service: AuditService, action: str) -> None:
    # TODO: 使用 pytest.raises 验证每个无效输入。
    raise NotImplementedError


def test_export_records_uses_a_temporary_path(
    tmp_path: Path,
    audit_service: AuditService,
) -> None:
    # TODO: 写入 tmp_path 下的 JSONL 文件，并解析内容验证字段，而非比较整段字符串。
    _ = export_records
    raise NotImplementedError


def test_channel_can_be_controlled_at_the_environment_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # TODO: 用 monkeypatch 设置 AUDIT_CHANNEL，验证 audit_channel()，不要直接改 os.environ。
    _ = audit_channel
    raise NotImplementedError


def test_service_emits_a_structured_log_event(
    caplog: pytest.LogCaptureFixture,
    fixed_now: datetime,
) -> None:
    # TODO: 捕获 INFO 日志，只验证事件名和 action 字段，不断言时间戳或整行格式。
    raise NotImplementedError


def test_service_calls_sink_using_a_spec_mock(fixed_now: datetime) -> None:
    # TODO: 创建 Mock(spec=AuditSink)，注入服务并用调用断言验证边界交互。
    # 保留这行类型提示，避免把一个没有 save() 的任意 mock 当成有效依赖。
    sink = Mock(spec=AuditSink)
    _ = sink
    raise NotImplementedError


async def test_cancelling_executor_waits_for_worker_cleanup() -> None:
    # TODO: 使用 asyncio.Event 协调 started/cleanup；取消 run_limited 的外层任务，
    # 验证 CancelledError 继续传播，且 worker 的 finally 已经执行。不要用长时间 sleep。
    _ = asyncio.Event
    _ = run_limited
    raise NotImplementedError
