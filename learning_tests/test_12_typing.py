import inspect

from learning_tests.loader import load_exercise


exercise = load_exercise("12_typing.py")
Cache = exercise["Cache"]
traced = exercise["traced"]


def test_cache_preserves_key_value_behavior() -> None:
    cache = Cache()
    assert cache.get("missing") is None
    cache.put("answer", 42)
    assert cache.get("answer") == 42


def test_traced_calls_callback_and_preserves_metadata() -> None:
    calls: list[str] = []

    @traced(calls.append)
    def greet(name: str, *, punctuation: str = "!") -> str:
        """Return a greeting."""

        return f"Hello {name}{punctuation}"

    assert greet("Ada", punctuation=".") == "Hello Ada."
    assert calls == ["greet"]
    assert greet.__name__ == "greet"
    assert greet.__doc__ == "Return a greeting."
    assert list(inspect.signature(greet).parameters) == ["name", "punctuation"]
