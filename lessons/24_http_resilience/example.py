"""第 24 章：有界重试、退避与总 deadline。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """只计算重试决策，不负责休眠或发送请求。"""

    max_attempts: int = 3
    retryable_methods: frozenset[str] = field(
        default_factory=lambda: frozenset({"GET", "HEAD", "OPTIONS"})
    )
    retryable_statuses: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 502, 503, 504})
    )
    base_delay: float = 0.1
    max_delay: float = 2.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts 至少为 1")
        if self.base_delay < 0 or self.max_delay < 0:
            raise ValueError("退避时间不能为负数")
        if self.base_delay > self.max_delay:
            raise ValueError("base_delay 不能大于 max_delay")

    def should_retry(
        self,
        method: str,
        status: int,
        *,
        attempt: int,
        idempotency_key: str | None = None,
    ) -> bool:
        """``attempt`` 是刚完成的尝试序号，从 1 开始。"""

        if attempt < 1:
            raise ValueError("attempt 从 1 开始")
        method = method.upper()
        has_idempotency_key = bool(idempotency_key and idempotency_key.strip())
        replayable = method in self.retryable_methods or has_idempotency_key
        return attempt < self.max_attempts and replayable and status in self.retryable_statuses

    def backoff_delay(self, *, attempt: int, jitter: float = 0.0) -> float:
        if attempt < 1:
            raise ValueError("attempt 从 1 开始")
        if jitter < 0:
            raise ValueError("jitter 不能为负数")
        delay = self.base_delay * float(2 ** (attempt - 1)) + jitter
        return min(self.max_delay, delay)


def parse_retry_after(value: str | None, *, now: datetime | None = None) -> float | None:
    """把 ``Retry-After`` 的秒数或 HTTP-date 转成非负等待秒数。"""

    if value is None:
        return None
    normalized = value.strip()
    if normalized.isascii() and normalized.isdigit():
        return float(normalized)
    try:
        retry_at = parsedate_to_datetime(normalized)
    except (TypeError, ValueError, OverflowError):
        return None
    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=UTC)
    reference = now or datetime.now(UTC)
    if reference.tzinfo is None:
        raise ValueError("now 必须包含时区")
    return max(0.0, (retry_at - reference).total_seconds())


def retry_delay_with_deadline(
    policy: RetryPolicy,
    *,
    attempt: int,
    elapsed: float,
    total_deadline: float,
    retry_after: str | None = None,
    now: datetime | None = None,
    jitter: float = 0.0,
) -> float | None:
    """返回下一次等待时间；没有剩余执行预算时返回 ``None``。"""

    if elapsed < 0:
        raise ValueError("elapsed 不能为负数")
    if total_deadline <= 0:
        raise ValueError("total_deadline 必须大于零")
    remaining = total_deadline - elapsed
    if remaining <= 0:
        return None

    delay = policy.backoff_delay(attempt=attempt, jitter=jitter)
    server_delay = parse_retry_after(retry_after, now=now)
    if server_delay is not None:
        delay = max(delay, server_delay)
    return delay if delay < remaining else None
