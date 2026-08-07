"""第 16 章练习：观察模块、包资源与已安装 distribution。

完成后运行 ``pytest lessons/16_packaging/test_lesson.py``。这些函数不能依赖当前
工作目录，也不要通过手工修改 ``sys.path`` 让导入碰巧成功。
"""

from __future__ import annotations


def module_facts(module_name: str) -> dict[str, str | None]:
    """返回 __name__、__package__、__file__、spec_name 和 origin。"""

    # TODO: 使用 importlib 导入模块，并从模块对象及其 __spec__ 提取信息。
    raise NotImplementedError


def import_is_cached(module_name: str) -> bool:
    """判断连续两次导入是否得到同一个模块对象。"""

    # TODO: 不要比较模块名称或文件路径，直接比较两次导入得到的对象身份。
    raise NotImplementedError


def read_resource_text(package: str, relative_path: str) -> str:
    """以 UTF-8 读取包内文本资源并去除首尾空白。"""

    # TODO: 使用 importlib.resources；不能从 Path.cwd() 拼接源码路径。
    raise NotImplementedError


def distribution_version(distribution_name: str) -> str:
    """返回已安装 distribution 的版本。"""

    # TODO: 使用 importlib.metadata；注意 distribution 名称可能不同于导入包名。
    raise NotImplementedError
