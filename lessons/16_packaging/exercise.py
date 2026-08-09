"""第 16 章练习：观察模块、包资源与已安装 distribution。

完成后运行 ``pytest lessons/16_packaging/test_lesson.py``。这些函数不能依赖当前
工作目录，也不要通过手工修改 ``sys.path`` 让导入碰巧成功。
"""

from __future__ import annotations

from importlib import import_module
from importlib.metadata import version
from importlib.resources import files


def module_facts(module_name: str) -> dict[str, str | None]:
    """返回 __name__、__package__、__file__、spec_name 和 origin。"""

    module = import_module(module_name)
    spec = module.__spec__

    return {
        "__name__": module.__name__,
        "__package__": module.__package__,
        "__file__": getattr(module, "__file__", None),
        "spec_name": spec.name if spec is not None else None,
        "origin": spec.origin if spec is not None else None,
    }


def import_is_cached(module_name: str) -> bool:
    """判断连续两次导入是否得到同一个模块对象。"""

    module_a = import_module(module_name)
    module_b = import_module(module_name)
    return module_a is module_b


def read_resource_text(package: str, relative_path: str) -> str:
    """以 UTF-8 读取包内文本资源并去除首尾空白。"""

    resource = files(package).joinpath(relative_path)
    return resource.read_text(encoding="utf-8").strip()


def distribution_version(distribution_name: str) -> str:
    """返回已安装 distribution 的版本。"""

    return version(distribution_name)


if __name__ == "__main__":
    facts = module_facts("json")
    for key, value in facts.items():
        print(f"{key}: {value}")
