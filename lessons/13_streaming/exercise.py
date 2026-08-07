"""第 13 章练习：流式读取 JSONL 并按批次返回 Event。"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError


class Event(BaseModel):
    name: str = Field(min_length=1)
    value: int


class InvalidRecord(ValueError):
    def __init__(self, path: Path, line_number: int, reason: str) -> None:
        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"{path}:{line_number}: {reason}")


def validated_batches(path: Path, batch_size: int) -> Iterator[list[Event]]:
    """空行跳过；JSON 或模型错误转换为带行号的 InvalidRecord。"""

    if batch_size <= 0:
        raise ValueError("batch_size 必须大于 0")

    def generator() -> Iterator[list[Event]]:
        batch: list[Event] = []
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    event = Event.model_validate(payload)
                except (json.JSONDecodeError, ValidationError) as error:
                    raise InvalidRecord(
                        path=path, line_number=line_number, reason=str(error)
                    ) from error
                batch.append(event)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

    return generator()
