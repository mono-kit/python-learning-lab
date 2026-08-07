"""按 ``course.toml`` 加载本章练习或参考实现。"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from runpy import run_path
from typing import Any

ROOT = Path(__file__).parents[1]
TARGET_ENV = "PYTHON_LEARNING_LAB_TARGET"


def _chapters_by_directory() -> dict[str, dict[str, object]]:
    course = tomllib.loads((ROOT / "course.toml").read_text(encoding="utf-8"))
    chapters = course["chapters"]
    assert isinstance(chapters, list)
    return {
        Path(str(chapter["courseware"])).parent.name: chapter
        for chapter in chapters
        if isinstance(chapter, dict)
    }


def load_file(relative_path: str) -> dict[str, Any]:
    """执行仓库内的一个 Python 文件并返回其全局命名空间。"""

    path = (ROOT / relative_path).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"路径必须位于仓库内：{relative_path}")
    return run_path(path)


def load_exercise(lesson: str) -> dict[str, Any]:
    """默认加载练习；Nox 可通过环境变量改为验证参考实现。"""

    target = os.environ.get(TARGET_ENV, "exercise")
    field = {"exercise": "exercise", "solution": "solution"}.get(target)
    if field is None:
        raise RuntimeError(f"{TARGET_ENV} 必须是 exercise 或 solution，而不是 {target!r}")

    try:
        chapter = _chapters_by_directory()[lesson]
        relative_path = str(chapter[field])
    except KeyError as error:
        raise RuntimeError(f"{lesson} 没有可加载的 {field}") from error
    return load_file(relative_path)
