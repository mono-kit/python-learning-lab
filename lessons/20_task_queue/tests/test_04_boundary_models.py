"""里程碑 4：Pydantic 只处理输入输出边界。"""

import pytest
from pydantic import ValidationError

from lessons._shared.task_queue.domain import Task
from lessons._shared.task_queue.models import CreateTaskInput, TaskOutput


def test_create_input_normalizes_and_rejects_invalid_external_data() -> None:
    incoming = CreateTaskInput.model_validate({"title": "  build wheel  "})
    assert incoming.title == "build wheel"

    with pytest.raises(ValidationError):
        CreateTaskInput.model_validate({"title": " "})
    with pytest.raises(ValidationError):
        CreateTaskInput.model_validate({"title": "valid", "unknown": True})


def test_output_model_maps_domain_state_without_mutating_domain() -> None:
    failed = Task("task-1", "publish").start().fail("network unavailable")

    output = TaskOutput.from_domain(failed)

    assert output.model_dump() == {
        "id": "task-1",
        "title": "publish",
        "status": "failed",
        "error": "network unavailable",
    }
    assert failed.error == "network unavailable"
