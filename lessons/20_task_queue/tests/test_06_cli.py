"""里程碑 6：CLI 解析契约；缺失接口时给出下一步提示。"""

from argparse import ArgumentParser
from importlib import import_module
from types import ModuleType

import pytest


def require_cli_module() -> ModuleType:
    module_name = "lessons._shared.task_queue.cli"
    try:
        module = import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name != module_name:
            raise
        module = None

    if module is None:
        pytest.fail(
            "里程碑 6 尚未实现：请新增 task_queue/cli.py，并公开 build_parser() "
            "与 main(argv=None) -> int；parser 需支持 add/list/run/retry/cancel。"
            "详见 lessons/20_task_queue/tests/README.md。",
            pytrace=False,
        )

    missing = [
        name for name in ("build_parser", "main") if not callable(getattr(module, name, None))
    ]
    if missing:
        pytest.fail(
            f"task_queue.cli 缺少可调用接口：{', '.join(missing)}。"
            "最小接口是 build_parser() 和 main(argv=None) -> int。",
            pytrace=False,
        )
    return module


def test_cli_parser_exposes_minimum_command_contract() -> None:
    module = require_cli_module()
    parser = module.build_parser()
    assert isinstance(parser, ArgumentParser)

    added = parser.parse_args(["add", "生成日报"])
    listed = parser.parse_args(["list"])
    run = parser.parse_args(["run", "--workers", "3", "--timeout", "10"])
    retried = parser.parse_args(["retry", "task-1"])
    cancelled = parser.parse_args(["cancel", "task-2"])

    assert (added.command, added.title) == ("add", "生成日报")
    assert listed.command == "list"
    assert (run.command, run.workers, run.timeout) == ("run", 3, 10.0)
    assert (retried.command, retried.task_id) == ("retry", "task-1")
    assert (cancelled.command, cancelled.task_id) == ("cancel", "task-2")


def test_cli_help_lists_all_commands(capsys: pytest.CaptureFixture[str]) -> None:
    module = require_cli_module()
    try:
        result = module.main(["--help"])
    except SystemExit as error:
        result = error.code

    assert result == 0
    output = capsys.readouterr().out
    for command in ["add", "list", "run", "retry", "cancel"]:
        assert command in output
