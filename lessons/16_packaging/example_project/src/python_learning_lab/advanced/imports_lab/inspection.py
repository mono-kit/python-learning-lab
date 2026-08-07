"""导入实验的无副作用实现。"""

from __future__ import annotations

import importlib
import importlib.util
from importlib.metadata import version
from importlib.resources import files


def module_facts(module_name: str) -> dict[str, str | None]:
    module = importlib.import_module(module_name)
    spec = module.__spec__
    return {
        "__name__": module.__name__,
        "__package__": module.__package__,
        "__file__": getattr(module, "__file__", None),
        "spec_name": spec.name if spec is not None else None,
        "origin": spec.origin if spec is not None else None,
    }


def import_is_cached(module_name: str) -> bool:
    first = importlib.import_module(module_name)
    second = importlib.import_module(module_name)
    return first is second


def can_import(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def read_resource_text(package: str, relative_path: str) -> str:
    """通过 import package 读取资源，不依赖当前工作目录。"""

    return files(package).joinpath(relative_path).read_text(encoding="utf-8").strip()


def distribution_version(distribution_name: str) -> str:
    """读取已安装 distribution 的版本；名称不必等于 import package。"""

    return version(distribution_name)


def welcome_text() -> str:
    return read_resource_text(
        "python_learning_lab.advanced.imports_lab",
        "resources/welcome.txt",
    )
