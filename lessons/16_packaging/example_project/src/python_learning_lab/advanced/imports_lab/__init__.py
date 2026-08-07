"""第 16 章：模块、包、导入缓存、包内资源和 distribution 元数据。"""

from .inspection import (
    distribution_version,
    import_is_cached,
    module_facts,
    read_resource_text,
    welcome_text,
)

__all__ = [
    "distribution_version",
    "import_is_cached",
    "module_facts",
    "read_resource_text",
    "welcome_text",
]
