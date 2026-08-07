import asyncio
import hashlib

import httpx
import pytest

from lessons._loader import load_exercise

exercise = load_exercise("23_async_http")
FetchResult = exercise["FetchResult"]
fetch_many = exercise["fetch_many"]
stream_sha256 = exercise["stream_sha256"]


async def test_fetch_many_limits_concurrency_and_preserves_order() -> None:
    active = 0
    maximum = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        try:
            await asyncio.sleep(0)
            if request.url.path == "/fail":
                return httpx.Response(503, json={"error": "busy"})
            return httpx.Response(200, json={"path": request.url.path})
        finally:
            active -= 1

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
    ) as client:
        results = await fetch_many(["/a", "/fail", "/b"], client, max_concurrency=2)

    assert [result.url for result in results] == ["/a", "/fail", "/b"]
    assert results[0].payload == {"path": "/a"}
    assert results[1].status == 503
    assert results[1].error == "http: 503"
    assert results[0].succeeded
    assert not results[1].succeeded
    assert maximum == 2


async def test_stream_sha256_does_not_require_a_real_network() -> None:
    content = b"streamed-content"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        digest = await stream_sha256(client, "https://example.test/file")

    assert digest == hashlib.sha256(content).hexdigest()


async def test_fetch_many_distinguishes_timeout_transport_and_json_failures() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/timeout":
            raise httpx.ReadTimeout("read stalled", request=request)
        if request.url.path == "/transport":
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200, content=b"not-json")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
    ) as client:
        results = await fetch_many(["/timeout", "/transport", "/json"], client)

    assert results[0].status is None
    assert results[0].error == "timeout: read stalled"
    assert results[1].status is None
    assert results[1].error == "transport: ConnectError"
    assert results[2].status == 200
    assert results[2].error is not None
    assert results[2].error.startswith("json:")
    assert all(not result.succeeded for result in results)


async def test_fetch_many_rejects_invalid_limit_and_propagates_cancellation() -> None:
    client_started = asyncio.Event()

    async def blocking_handler(_request: httpx.Request) -> httpx.Response:
        client_started.set()
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(blocking_handler),
        base_url="https://example.test",
    ) as client:
        with pytest.raises(ValueError):
            await fetch_many(["/a"], client, max_concurrency=0)

        task = asyncio.create_task(fetch_many(["/a", "/b"], client))
        await client_started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


def test_fetch_result_success_does_not_depend_on_payload_truthiness() -> None:
    assert FetchResult(url="/empty", payload=None).succeeded
    assert not FetchResult(url="/failed", error="boom").succeeded
