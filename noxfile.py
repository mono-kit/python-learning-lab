"""可重复工程任务。

推荐通过 ``uvx nox --list`` 运行；Nox 负责编排，uv 优先负责创建 session 环境。
所有发布相关 session 都只验证，不会上传到包索引。
"""

from __future__ import annotations

import shutil
import tarfile
import zipfile
from pathlib import Path

import nox

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
EGG_INFO = ROOT / "lessons/16_packaging/example_project/src/python_learning_lab.egg-info"
COURSE_PATHS = [
    "lessons",
    "tests",
    "noxfile.py",
]
TYPED_EXAMPLES = [
    "lessons/10_data_model/example.py",
    "lessons/11_descriptors/example.py",
    "lessons/12_typing/example.py",
    "lessons/13_streaming/example.py",
    "lessons/14_concurrency/example.py",
    "lessons/15_testing/example.py",
    "lessons/16_packaging/example_project/src/python_learning_lab",
    "lessons/_shared/task_queue",
    "lessons/19_performance/example.py",
    "lessons/21_http_stdlib/example.py",
    "lessons/22_http_clients/example.py",
    "lessons/23_async_http/example.py",
    "lessons/24_http_resilience/example.py",
    "lessons/25_asgi_protocol/example.py",
    "lessons/26_asgi_service/example.py",
]
SOLUTION_TESTS = [
    str(path.relative_to(ROOT))
    for path in sorted((ROOT / "lessons").glob("*/test_lesson.py"))
    if path.parent.name != "15_testing"
]

nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = ["lint", "typing", "tests-3.11", "solution-tests"]


@nox.session
def lint(session: nox.Session) -> None:
    """运行 Ruff 代码检查和格式检查。"""

    session.install("ruff>=0.9")
    session.run("ruff", "check", *COURSE_PATHS)
    session.run("ruff", "format", "--check", *COURSE_PATHS)


@nox.session
def typing(session: nox.Session) -> None:
    """严格检查高级语言和工程示例的公共类型边界。"""

    session.install("-e", ".[web]", "mypy>=1.11")
    for example in TYPED_EXAMPLES:
        session.run("mypy", "--strict", example)


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    """在项目声明支持的 Python 版本中运行回归测试。"""

    session.install("-e", ".[dev,web]")
    session.run("pytest", *session.posargs)


@nox.session
def exercise(session: nox.Session) -> None:
    """只运行指定章节测试，例如 ``-- lessons/10_data_model/test_lesson.py``。"""

    if not session.posargs:
        session.error("请在 -- 后指定一个 lessons/*/test_lesson.py 文件")
    session.install("-e", ".[dev,web]")
    session.run("pytest", *session.posargs)


@nox.session(name="solution-tests")
def solution_tests(session: nox.Session) -> None:
    """用同一组学习测试验证参考答案，防止题目、测试和答案漂移。"""

    session.install("-e", ".[dev,web]")
    session.run(
        "pytest",
        *SOLUTION_TESTS,
        env={"PYTHON_LEARNING_LAB_TARGET": "solution"},
    )
    session.run("pytest", "lessons/15_testing/reference_test.py")


def build_and_check(session: nox.Session, *, wheel_only: bool = False) -> list[Path]:
    for generated in (DIST, BUILD, EGG_INFO):
        shutil.rmtree(generated, ignore_errors=True)
    session.install("build>=1.2", "twine>=6")
    command = ["python", "-m", "build"]
    if wheel_only:
        command.append("--wheel")
    session.run(*command)
    artifacts = sorted(DIST.iterdir())
    session.run("twine", "check", *(str(path) for path in artifacts))
    wheel = next(path for path in artifacts if path.suffix == ".whl")
    check_wheel_runtime_files(session, wheel)
    if not wheel_only:
        sdist = next(path for path in artifacts if path.name.endswith(".tar.gz"))
        check_sdist_course_assets(session, sdist)
    for generated in (BUILD, EGG_INFO):
        shutil.rmtree(generated, ignore_errors=True)
    return artifacts


def check_wheel_runtime_files(session: nox.Session, wheel: Path) -> None:
    """wheel 只发布第 16 章声明的最小示例包，不携带整套课程源码。"""

    expected_package_files = {
        "python_learning_lab/__init__.py",
        "python_learning_lab/__main__.py",
        "python_learning_lab/advanced/__init__.py",
        "python_learning_lab/advanced/imports_lab/__init__.py",
        "python_learning_lab/advanced/imports_lab/__main__.py",
        "python_learning_lab/advanced/imports_lab/inspection.py",
        "python_learning_lab/advanced/imports_lab/resources/welcome.txt",
    }
    with zipfile.ZipFile(wheel) as archive:
        package_files = {
            name for name in archive.namelist() if name.startswith("python_learning_lab/")
        }
    unexpected = sorted(package_files - expected_package_files)
    missing = sorted(expected_package_files - package_files)
    if unexpected or missing:
        session.error(f"wheel 文件不符合最小运行时范围：unexpected={unexpected}, missing={missing}")


def check_sdist_course_assets(session: nox.Session, sdist: Path) -> None:
    """课程型项目的源码包必须包含讲义、练习、测试、答案与清单。"""

    required = {
        "AGENTS.md",
        "course.toml",
        "lessons/01_basics/lesson.md",
        "lessons/15_testing/exercise.md",
        "lessons/15_testing/lesson.md",
        "lessons/15_testing/test_lesson.py",
        "lessons/20_task_queue/tests/README.md",
        "lessons/26_asgi_service/test_lesson.py",
        "reviews/14_concurrency.md",
        "lessons/15_testing/example.py",
        "lessons/15_testing/reference_test.py",
        (
            "lessons/16_packaging/example_project/src/python_learning_lab/advanced/"
            "imports_lab/resources/welcome.txt"
        ),
        "lessons/_shared/task_queue/domain.py",
    }
    with tarfile.open(sdist) as archive:
        members = {
            "/".join(Path(name).parts[1:])
            for name in archive.getnames()
            if len(Path(name).parts) > 1
        }
    missing = sorted(required - members)
    if missing:
        session.error(f"sdist 缺少课程资产：{', '.join(missing)}")


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
    session.notify("solution-tests")
    session.notify("build")
    session.notify("package_smoke")
    session.log("已安排全部验证 session；本流程不会发布任何产物。")
