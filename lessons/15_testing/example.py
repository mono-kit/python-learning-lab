"""第 15 章：为测试提供确定性边界，而不是把 mock 铺满业务代码。

这个模块故意保持业务规则很小，让练习把注意力放在 pytest 本身：可注入时钟、
可观察的 fake、只验证交互的 mock、环境变量边界、日志和临时文件。
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class FrozenClock:
    current: datetime

    def now(self) -> datetime:
        return self.current


@dataclass(frozen=True, slots=True)
class AuditRecord:
    action: str
    occurred_at: datetime


class AuditSink(Protocol):
    """保存审计记录的最小边界，适合使用 fake 或带 spec 的 mock。"""

    def save(self, record: AuditRecord) -> None: ...


class MemoryAuditSink:
    """保存可查询状态的 fake；它不模拟调用细节。"""

    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def save(self, record: AuditRecord) -> None:
        self.records.append(record)


class AuditService:
    def __init__(
        self,
        clock: Clock,
        sink: AuditSink | None = None,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self.clock = clock
        self.sink = sink
        self.logger = logger or logging.getLogger(__name__)

    def record(self, action: str) -> AuditRecord:
        if not action.strip():
            raise ValueError("action 不能为空")
        record = AuditRecord(action.strip(), self.clock.now())
        if self.sink is not None:
            self.sink.save(record)
        self.logger.info("audit_recorded", extra={"action": record.action})
        return record


def audit_channel() -> str:
    """从进程环境读取边界配置，供 ``monkeypatch`` 练习使用。"""

    return os.environ.get("AUDIT_CHANNEL", "local")


def export_records(path: Path, records: Iterable[AuditRecord]) -> None:
    """把记录写为 JSON Lines；测试应使用 ``tmp_path``，而非固定路径。"""

    lines = [
        json.dumps(
            {"action": record.action, "occurred_at": record.occurred_at.isoformat()},
            ensure_ascii=False,
        )
        for record in records
    ]
    text = "\n".join(lines)
    path.write_text(f"{text}\n" if text else "", encoding="utf-8")
