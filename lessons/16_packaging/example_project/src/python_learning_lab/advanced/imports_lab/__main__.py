"""使用 ``python -m python_learning_lab.advanced.imports_lab`` 运行。"""

from .inspection import import_is_cached, module_facts, welcome_text


def main() -> None:
    facts = module_facts(__package__ or "python_learning_lab.advanced.imports_lab")
    for key, value in facts.items():
        print(f"{key}: {value}")
    print(f"重复导入复用同一对象：{import_is_cached('json')}")
    print(welcome_text())


if __name__ == "__main__":
    main()
