"""第 15 章：为测试提供确定性边界，而不是把 mock 铺满业务代码。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
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


class AuditService:
    def __init__(self, clock: Clock) -> None:
        self.clock = clock

    def record(self, action: str) -> AuditRecord:
        if not action.strip():
            raise ValueError("action 不能为空")
        return AuditRecord(action.strip(), self.clock.now())
