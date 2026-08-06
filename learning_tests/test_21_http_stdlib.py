from learning_tests.loader import load_exercise

exercise = load_exercise("21_http_stdlib.py")
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
