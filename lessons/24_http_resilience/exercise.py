"""第 24 章练习：显式表达有限重试和指数退避。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RetryPolicy:
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
        # TODO: max_attempts 至少为 1；退避值不能为负；base_delay 不能大于 max_delay。
        pass

    def should_retry(
        self,
        method: str,
        status: int,
        *,
        attempt: int,
        idempotency_key: str | None = None,
    ) -> bool:
        # TODO: 尝试次数必须有上限；POST 只有提供幂等键时才允许重放。
        raise NotImplementedError

    def backoff_delay(self, *, attempt: int, jitter: float = 0.0) -> float:
        # TODO: 计算 min(max_delay, base_delay * 2 ** (attempt - 1) + jitter)。
        raise NotImplementedError


def parse_retry_after(value: str | None, *, now: datetime | None = None) -> float | None:
    """解析 delay-seconds 或 HTTP-date；无效 header 返回 None。"""

    # TODO: HTTP-date 需要与带时区的 now 比较，并把过去的时间限制为 0 秒。
    raise NotImplementedError


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
    """计算仍在总 deadline 内的下一次等待；无预算时返回 None。"""

    # TODO: 取客户端 backoff 与 Retry-After 的较大值，但不能耗尽全部剩余预算。
    raise NotImplementedError
