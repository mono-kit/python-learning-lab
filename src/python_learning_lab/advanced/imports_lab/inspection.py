"""导入实验的无副作用实现。"""

from __future__ import annotations

import importlib
import importlib.util
from importlib.resources import files


def module_facts(module_name: str) -> dict[str, str | None]:
    module = importlib.import_module(module_name)
    spec = module.__spec__
    return {
        "__name__": module.__name__,
        "__package__": module.__package__,
        "__file__": getattr(module, "__file__", None),
        "origin": spec.origin if spec is not None else None,
    }


def import_is_cached(module_name: str) -> bool:
    first = importlib.import_module(module_name)
    second = importlib.import_module(module_name)
    return first is second


def can_import(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def welcome_text() -> str:
    resource = files("python_learning_lab.advanced.imports_lab").joinpath("resources/welcome.txt")
    return resource.read_text(encoding="utf-8").strip()
