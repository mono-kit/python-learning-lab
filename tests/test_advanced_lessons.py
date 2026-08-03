import asyncio
import json
from decimal import Decimal
from pathlib import Path

import pytest

from python_learning_lab.advanced.concurrency import run_limited
from python_learning_lab.advanced.data_model import (
    CurrencyMismatch,
    Inventory,
    Money,
    StockItem,
    Version,
)
from python_learning_lab.advanced.imports_lab import import_is_cached, welcome_text
from python_learning_lab.advanced.object_protocols import Account, Service
from python_learning_lab.advanced.performance import measure_peak_memory
from python_learning_lab.advanced.streaming import InvalidRecord, validated_batches
from python_learning_lab.advanced.typing_lab import Cache, has_email, traced


def test_money_is_an_immutable_hashable_value_object() -> None:
    ten = Money(Decimal("10.00"), "cny")
    equivalent = Money(Decimal(10), "CNY")

    assert ten == equivalent
    assert hash(ten) == hash(equivalent)
    assert len({ten, equivalent}) == 1
    assert f"{ten:.1f}" == "10.0 CNY"
    assert ten + Money(Decimal("2.50"), "CNY") == Money(Decimal("12.50"), "CNY")

    with pytest.raises(CurrencyMismatch):
        _ = ten + Money(Decimal(1), "USD")


def test_version_and_mapping_protocol() -> None:
    assert Version.parse("2.10.0") > Version.parse("2.9.9")
    inventory = Inventory([StockItem("keyboard", 2), StockItem("mouse", 3)])

    assert len(inventory) == 2
    assert "keyboard" in inventory
    assert inventory["mouse"].quantity == 3
    assert list(inventory) == ["keyboard", "mouse"]


def test_data_descriptors_and_cooperative_mro() -> None:
    account = Account("  Ada  ", 36)
    account.__dict__["age"] = 999

    assert account.name == "Ada"
    assert account.age == 36
    assert Service().process([]) == ["logging", "metrics", "handler"]


def test_generic_cache_type_guard_and_paramspec_decorator() -> None:
    cache: Cache[str, int] = Cache()
    cache.put("answer", 42)
    assert cache.get("answer") == 42

    row = {"id": 1, "name": "Ada", "email": "ada@example.com"}
    assert has_email(row)

    calls: list[str] = []

    @traced(calls.append)
    def add(left: int, right: int) -> int:
        return left + right

    assert add(2, 3) == 5
    assert calls == ["add"]


def test_streaming_pipeline_batches_and_reports_line_number(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    records = [
        {"name": "created", "value": 1},
        {"name": "updated", "value": 2},
        {"name": "deleted", "value": 3},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")

    batches = list(validated_batches(path, 2))
    assert [[event.name for event in batch] for batch in batches] == [
        ["created", "updated"],
        ["deleted"],
    ]

    path.write_text('{"name": "ok", "value": 1}\ninvalid\n', encoding="utf-8")
    with pytest.raises(InvalidRecord) as captured:
        list(validated_batches(path, 2))
    assert captured.value.line_number == 2


async def test_bounded_concurrency_keeps_order_and_limit() -> None:
    active = 0
    maximum = 0

    async def worker(value: int) -> int:
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        try:
            await asyncio.sleep(0)
            return value**2
        finally:
            active -= 1

    results = await run_limited([3, 1, 2], worker, max_concurrency=2)
    assert [result.value for result in results] == [9, 1, 4]
    assert maximum == 2


def test_import_resource_and_memory_measurement() -> None:
    assert import_is_cached("json")
    assert "安装包内部" in welcome_text()

    result, memory = measure_peak_memory(lambda: [number**2 for number in range(100)])
    assert result[3] == 9
    assert memory.peak_bytes >= memory.current_bytes >= 0
