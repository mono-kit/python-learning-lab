import httpx
import pytest

from lessons._loader import load_exercise

exercise = load_exercise("22_http_clients")
SyncJSONClient = exercise["SyncJSONClient"]
InvalidJSONResponse = exercise["InvalidJSONResponse"]


def test_sync_client_reuses_injected_client_and_checks_contract() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path == "/object":
            return httpx.Response(200, json={"answer": 42})
        if request.url.path == "/list":
            return httpx.Response(200, json=[1, 2, 3])
        return httpx.Response(404, json={"detail": "missing"})

    with httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://example.test",
    ) as transport_client:
        client = SyncJSONClient(transport_client)
        assert client.get_object("/object") == {"answer": 42}
        with pytest.raises(InvalidJSONResponse):
            client.get_object("/list")
        with pytest.raises(httpx.HTTPStatusError):
            client.get_object("/missing")

    assert calls == ["/object", "/list", "/missing"]
