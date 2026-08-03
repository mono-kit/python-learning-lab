"""第 13 章：惰性数据管道、生成器清理和动态资源管理。"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import TextIO

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
    """逐行验证 JSONL，不把整个文件一次性读入内存。

    参数检查位于外层普通函数，因此调用时立刻失败，而不是第一次 ``next()``
    时才失败。文件则由内层生成器延迟打开。
    """

    if batch_size <= 0:
        raise ValueError("batch_size 必须大于零")

    def generate() -> Iterator[list[Event]]:
        batch: list[Event] = []
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                    event = Event.model_validate(payload)
                except (json.JSONDecodeError, ValidationError) as error:
                    raise InvalidRecord(path, line_number, str(error)) from error
                batch.append(event)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
            if batch:
                yield batch

    return generate()


@contextmanager
def open_texts(paths: Sequence[Path]) -> Iterator[list[TextIO]]:
    """ExitStack 适合管理运行时才知道数量的上下文管理器。"""

    with ExitStack() as stack:
        streams: list[TextIO] = []
        for path in paths:
            streams.append(stack.enter_context(path.open(encoding="utf-8")))
        yield streams


def main() -> None:
    print("请在练习中用 tmp_path 创建 JSONL 文件，再消费 validated_batches。")


if __name__ == "__main__":
    main()
