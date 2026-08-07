"""第 15 章参考测试：pytest fixture、替身、边界和异步取消。"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
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
    return datetime(2026, 8, 6, 9, 30, tzinfo=UTC)


@pytest.fixture
def memory_sink() -> MemoryAuditSink:
    return MemoryAuditSink()


@pytest.fixture
def audit_service(fixed_now: datetime, memory_sink: MemoryAuditSink) -> AuditService:
    return AuditService(FrozenClock(fixed_now), memory_sink)


def test_service_records_normalized_action_in_fake(
    audit_service: AuditService,
    memory_sink: MemoryAuditSink,
    fixed_now: datetime,
) -> None:
    record = audit_service.record("  deploy  ")

    assert record.action == "deploy"
    assert record.occurred_at == fixed_now
    assert memory_sink.records == [record]


@pytest.mark.parametrize("action", ["", "   ", "\n\t"], ids=["empty", "spaces", "newline"])
def test_service_rejects_blank_actions(audit_service: AuditService, action: str) -> None:
    with pytest.raises(ValueError, match="action 不能为空"):
        audit_service.record(action)


def test_export_records_uses_a_temporary_path(
    tmp_path: Path,
    audit_service: AuditService,
) -> None:
    path = tmp_path / "audit.jsonl"
    record = audit_service.record("发布")

    export_records(path, [record])

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == {"action": "发布", "occurred_at": record.occurred_at.isoformat()}


def test_channel_can_be_controlled_at_the_environment_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUDIT_CHANNEL", "ci")

    assert audit_channel() == "ci"


def test_service_emits_a_structured_log_event(
    caplog: pytest.LogCaptureFixture,
    fixed_now: datetime,
) -> None:
    caplog.set_level(logging.INFO)

    AuditService(FrozenClock(fixed_now)).record("deploy")

    record = next(item for item in caplog.records if item.message == "audit_recorded")
    assert record.action == "deploy"


def test_service_calls_sink_using_a_spec_mock(fixed_now: datetime) -> None:
    sink = Mock(spec=AuditSink)
    service = AuditService(FrozenClock(fixed_now), sink)

    record = service.record("deploy")

    sink.save.assert_called_once_with(record)


async def test_cancelling_executor_waits_for_worker_cleanup() -> None:
    started = asyncio.Event()
    cleanup_finished = asyncio.Event()
    release = asyncio.Event()

    async def worker(value: int) -> int:
        started.set()
        try:
            await release.wait()
            return value
        finally:
            cleanup_finished.set()

    execution = asyncio.create_task(run_limited([1], worker, max_concurrency=1))
    await asyncio.wait_for(started.wait(), timeout=1)

    execution.cancel()
    with pytest.raises(asyncio.CancelledError):
        await execution

    assert cleanup_finished.is_set()
