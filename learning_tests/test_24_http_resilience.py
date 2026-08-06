from learning_tests.loader import load_exercise

exercise = load_exercise("24_http_resilience.py")
RetryPolicy = exercise["RetryPolicy"]


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
