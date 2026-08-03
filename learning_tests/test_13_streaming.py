import json
from pathlib import Path

import pytest

from learning_tests.loader import load_exercise


exercise = load_exercise("13_streaming.py")
validated_batches = exercise["validated_batches"]
InvalidRecord = exercise["InvalidRecord"]


def write_jsonl(path: Path, records: list[object]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records),
        encoding="utf-8",
    )


def test_validated_batches_is_lazy_and_keeps_final_partial_batch(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    write_jsonl(
        path,
        [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2},
            {"name": "c", "value": 3},
        ],
    )

    batches = validated_batches(path, 2)
    assert [[event.name for event in batch] for batch in batches] == [["a", "b"], ["c"]]


def test_batch_size_is_checked_before_iteration(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        validated_batches(tmp_path / "does-not-need-to-exist", 0)


def test_invalid_record_contains_line_number(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    path.write_text('{"name": "ok", "value": 1}\nnot-json\n', encoding="utf-8")

    with pytest.raises(InvalidRecord) as captured:
        list(validated_batches(path, 10))

    assert captured.value.line_number == 2
    assert captured.value.path == path
