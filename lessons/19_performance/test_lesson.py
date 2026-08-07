import tracemalloc

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("19_performance")
benchmark = exercise["benchmark"]
profile_text = exercise["profile_text"]
measure_peak_memory = exercise["measure_peak_memory"]


def test_benchmark_runs_the_callable_exactly_the_requested_number_of_times() -> None:
    calls = 0

    def operation() -> None:
        nonlocal calls
        calls += 1

    elapsed = benchmark(operation, number=7)

    assert calls == 7
    assert elapsed >= 0


@pytest.mark.parametrize("number", [0, -1])
def test_benchmark_rejects_non_positive_repeat_counts(number: int) -> None:
    with pytest.raises(ValueError, match="number"):
        benchmark(lambda: None, number=number)


def test_profile_text_forwards_arguments_and_names_the_profiled_function() -> None:
    observed: list[int] = []

    def total(values: list[int], *, scale: int) -> int:
        observed.extend(values)
        return sum(values) * scale

    report = profile_text(total, [1, 2, 3], scale=2)

    assert observed == [1, 2, 3]
    assert "total" in report
    assert "function calls" in report
    assert "cumulative" in report


def test_memory_measurement_preserves_the_result_and_reports_a_peak() -> None:
    result, memory = measure_peak_memory(lambda size: [value**2 for value in range(size)], 100)

    assert result[3] == 9
    assert len(result) == 100
    assert memory.peak_bytes >= memory.current_bytes >= 0


def test_memory_measurement_stops_tracing_when_the_function_fails() -> None:
    def fail() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        measure_peak_memory(fail)

    assert not tracemalloc.is_tracing()
