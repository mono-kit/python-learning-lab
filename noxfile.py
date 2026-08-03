"""可重复工程任务。

推荐通过 ``uvx nox --list`` 运行；Nox 负责编排，uv 优先负责创建 session 环境。
所有发布相关 session 都只验证，不会上传到包索引。
"""

from __future__ import annotations

import shutil
from pathlib import Path

import nox

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
COURSE_PATHS = [
    "src/python_learning_lab/advanced",
    "src/python_learning_lab/engineering",
    "src/python_learning_lab/task_queue",
    "tests/test_advanced_lessons.py",
    "tests/test_engineering_lessons.py",
    "noxfile.py",
]

nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = ["lint", "typing", "tests-3.11"]


@nox.session
def lint(session: nox.Session) -> None:
    """运行 Ruff 代码检查和格式检查。"""

    session.install("ruff>=0.9")
    session.run("ruff", "check", *COURSE_PATHS)
    session.run("ruff", "format", "--check", *COURSE_PATHS)


@nox.session
def typing(session: nox.Session) -> None:
    """严格检查高级语言和工程示例的公共类型边界。"""

    session.install("-e", ".", "mypy>=1.11")
    session.run(
        "mypy",
        "--strict",
        "src/python_learning_lab/advanced",
        "src/python_learning_lab/engineering",
        "src/python_learning_lab/task_queue",
    )


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    """在项目声明支持的 Python 版本中运行回归测试。"""

    session.install("-e", ".[dev]")
    session.run("pytest", *session.posargs)


@nox.session
def exercise(session: nox.Session) -> None:
    """只运行指定章节练习，例如 ``-- learning_tests/test_10_data_model.py``。"""

    if not session.posargs:
        session.error("请在 -- 后指定一个 learning_tests/test_*.py 文件")
    session.install("-e", ".[dev]")
    session.run("pytest", *session.posargs)


def build_and_check(session: nox.Session, *, wheel_only: bool = False) -> list[Path]:
    shutil.rmtree(DIST, ignore_errors=True)
    session.install("build>=1.2", "twine>=6")
    command = ["python", "-m", "build"]
    if wheel_only:
        command.append("--wheel")
    session.run(*command)
    artifacts = sorted(DIST.iterdir())
    session.run("twine", "check", *(str(path) for path in artifacts))
    return artifacts


@nox.session
def build(session: nox.Session) -> None:
    """构建 sdist/wheel 并检查发布元数据，不上传。"""

    build_and_check(session)


@nox.session
def package_smoke(session: nox.Session) -> None:
    """安装真实 wheel，并从源码目录外验证 import、资源和 CLI。"""

    artifacts = build_and_check(session, wheel_only=True)
    wheel = next(path for path in artifacts if path.suffix == ".whl")
    session.install("--force-reinstall", str(wheel))
    session.chdir(session.create_tmp())
    session.run(
        "python",
        "-c",
        "from python_learning_lab.advanced.imports_lab import welcome_text; "
        "assert '安装包内部' in welcome_text()",
    )
    session.run("python-learning-lab")


@nox.session
def release_check(session: nox.Session) -> None:
    """编排发布前门禁；明确不调用 twine upload 或 uv publish。"""

    session.notify("lint")
    session.notify("typing")
    session.notify("tests-3.11")
    session.notify("build")
    session.notify("package_smoke")
    session.log("已安排全部验证 session；本流程不会发布任何产物。")
