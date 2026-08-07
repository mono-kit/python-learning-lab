from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("24_http_resilience")
RetryPolicy = exercise["RetryPolicy"]
parse_retry_after = exercise["parse_retry_after"]
retry_delay_with_deadline = exercise["retry_delay_with_deadline"]


def test_retry_is_bounded_and_conservative_by_default() -> None:
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry("GET", 503, attempt=1)
    assert policy.should_retry("GET", 503, attempt=2)
    assert not policy.should_retry("GET", 503, attempt=3)
    assert not policy.should_retry("GET", 400, attempt=1)
    assert not policy.should_retry("POST", 503, attempt=1)
    assert policy.should_retry("POST", 503, attempt=1, idempotency_key="request-1")


def test_backoff_is_exponential_and_capped() -> None:
    policy = RetryPolicy(base_delay=0.25, max_delay=1.0)

    assert policy.backoff_delay(attempt=1) == 0.25
    assert policy.backoff_delay(attempt=2, jitter=0.1) == 0.6
    assert policy.backoff_delay(attempt=10) == 1.0


def test_policy_rejects_invalid_configuration_and_arguments() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        RetryPolicy(base_delay=-0.1)
    with pytest.raises(ValueError):
        RetryPolicy(base_delay=2.0, max_delay=1.0)

    policy = RetryPolicy()
    with pytest.raises(ValueError):
        policy.should_retry("GET", 503, attempt=0)
    with pytest.raises(ValueError):
        policy.backoff_delay(attempt=1, jitter=-0.1)


def test_retry_after_supports_seconds_and_http_date() -> None:
    now = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    later = format_datetime(now + timedelta(seconds=5), usegmt=True)

    assert parse_retry_after("3", now=now) == 3.0
    assert parse_retry_after(later, now=now) == 5.0
    assert parse_retry_after("not-a-date", now=now) is None


def test_retry_delay_respects_server_hint_and_total_deadline() -> None:
    policy = RetryPolicy(base_delay=0.25, max_delay=1.0)

    assert (
        retry_delay_with_deadline(
            policy,
            attempt=1,
            elapsed=0.5,
            total_deadline=3.0,
            retry_after="1",
        )
        == 1.0
    )
    assert (
        retry_delay_with_deadline(
            policy,
            attempt=1,
            elapsed=1.5,
            total_deadline=2.0,
            retry_after="1",
        )
        is None
    )
