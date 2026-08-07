# 第 16 章练习：从源码到可安装产物

按顺序完成并记录每一步观察：

1. 完成 `16_packaging.py`，并运行
   `uv run pytest lessons/16_packaging/test_lesson.py`。
2. 运行 `python file.py` 与 `python -m package.module`，比较包上下文。
3. 在 `sys.modules` 中找到本项目模块，证明重复导入复用同一对象。
4. 运行 `uv build`，检查 wheel 中的 Python 文件、资源和 dist-info。
5. 从 sdist 重新构建 wheel，确认没有依赖开发目录中的漏声明文件。
6. 用 `uvx nox -s package_smoke` 从源码目录外验证资源和 CLI。
7. 比较 setuptools 后端、uv 构建前端和 twine/uv 发布命令的职责。
8. 对照同目录的 `rye_migration/` 写出迁移前后字段映射。

本练习不要求向 TestPyPI 或 PyPI 上传。外部发布必须单独确认项目名、版本、索引
和凭据。
