"""第 16 章的最小可安装 CLI。"""

from .advanced.imports_lab import distribution_version, welcome_text


def main() -> None:
    """确认 distribution 元数据、包内资源和 console script 都可用。"""

    print("Python Learning Lab")
    print(f"version: {distribution_version('python-learning-lab')}")
    print(welcome_text())


if __name__ == "__main__":
    main()
