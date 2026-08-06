import asyncio
import hashlib

import pytest

httpx = pytest.importorskip("httpx")

from python_learning_lab.web.http_clients import (
    RetryPolicy,
    SyncJSONClient,
    fetch_many,
    stream_sha256,
)


def test_sync_client_uses_in_memory_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"path": request.url.path})

    with httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
    ) as transport_client:
        client = SyncJSONClient(transport_client)
        assert client.get_object("/users/1") == {"path": "/users/1"}


async def test_async_client_is_limited_ordered_and_streamed() -> None:
    active = 0
    maximum = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        try:
            await asyncio.sleep(0)
            return httpx.Response(200, json={"path": request.url.path})
        finally:
            active -= 1

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
    ) as client:
        results = await fetch_many(["/3", "/1", "/2"], client, max_concurrency=2)

    assert [result.payload["path"] for result in results] == ["/3", "/1", "/2"]
    assert maximum == 2

    content = b"large response represented by chunks"

    def stream_handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    async with httpx.AsyncClient(transport=httpx.MockTransport(stream_handler)) as client:
        assert (
            await stream_sha256(client, "https://example.test/file")
            == hashlib.sha256(content).hexdigest()
        )


def test_retry_policy_is_bounded() -> None:
    policy = RetryPolicy(max_attempts=3)

    assert policy.should_retry("GET", 503, attempt=1)
    assert not policy.should_retry("GET", 503, attempt=3)
    assert not policy.should_retry("POST", 503, attempt=1)
    assert policy.should_retry("POST", 503, attempt=1, idempotency_key="operation-1")
    assert not policy.should_retry("POST", 503, attempt=1, idempotency_key="   ")
