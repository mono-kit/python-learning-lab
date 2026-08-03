from pathlib import Path
from runpy import run_path
from typing import Any


ROOT = Path(__file__).parents[1]


def load_exercise(filename: str) -> dict[str, Any]:
    return run_path(ROOT / "exercises" / "advanced" / filename)
