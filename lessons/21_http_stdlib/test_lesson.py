import json
from http.client import HTTPConnection
from urllib.parse import urlsplit

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("21_http_stdlib")
HTTPStatusFailure = exercise["HTTPStatusFailure"]
request_json = exercise["request_json"]
running_server = exercise["running_server"]


def test_standard_library_server_and_client_exchange_json() -> None:
    with running_server() as base_url:
        health = request_json(f"{base_url}/health")
        echo = request_json(
            f"{base_url}/echo",
            method="POST",
            payload={"message": "你好"},
        )

    assert health.status == 200
    assert health.json() == {"status": "ok"}
    assert echo.status == 200
    assert echo.json() == {"echo": {"message": "你好"}}


def test_http_status_is_different_from_transport_failure() -> None:
    with running_server() as base_url:
        missing = request_json(f"{base_url}/missing")
        wrong_method = request_json(
            f"{base_url}/health",
            method="POST",
            payload={},
        )

    assert missing.status == 404
    assert missing.json() == {"error": "not found"}
    assert wrong_method.status == 405
    assert "GET" in wrong_method.headers["Allow"]

    with pytest.raises(HTTPStatusFailure) as caught:
        missing.raise_for_status()
    assert caught.value.response is missing


def test_query_target_and_invalid_json_are_handled_at_http_boundary() -> None:
    with running_server() as base_url:
        item = request_json(f"{base_url}/items?id=python%20book")

        target = urlsplit(base_url)
        connection = HTTPConnection(target.hostname, target.port, timeout=2)
        try:
            connection.request(
                "POST",
                "/echo",
                body=b"{",
                headers={"Content-Type": "application/json", "Content-Length": "1"},
            )
            raw_response = connection.getresponse()
            invalid_status = raw_response.status
            invalid_payload = json.loads(raw_response.read())
        finally:
            connection.close()

    assert item.json() == {"id": "python book"}
    assert invalid_status == 400
    assert invalid_payload == {"error": "invalid json"}


def test_echo_rejects_unsupported_media_type_and_oversized_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(request_json.__globals__, "MAX_BODY_BYTES", 8)

    with running_server() as base_url:
        oversized = request_json(
            f"{base_url}/echo",
            method="POST",
            payload={"message": "too long"},
        )

        target = urlsplit(base_url)
        connection = HTTPConnection(target.hostname, target.port, timeout=2)
        try:
            connection.request(
                "POST",
                "/echo",
                body=b"plain text",
                headers={"Content-Type": "text/plain"},
            )
            raw_response = connection.getresponse()
            media_type_status = raw_response.status
            raw_response.read()
        finally:
            connection.close()

    assert oversized.status == 413
    assert media_type_status == 415
