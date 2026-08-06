"""第 24 章练习：显式表达有限重试和指数退避。"""

from __future__ import annotations

from dataclasses import dataclass, field


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
