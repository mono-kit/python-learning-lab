import asyncio
import hashlib

import httpx

from learning_tests.loader import load_exercise

exercise = load_exercise("23_async_http.py")
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
    assert maximum == 2


async def test_stream_sha256_does_not_require_a_real_network() -> None:
    content = b"streamed-content"

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=content)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        digest = await stream_sha256(client, "https://example.test/file")

    assert digest == hashlib.sha256(content).hexdigest()
