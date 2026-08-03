# Rye 遗留项目迁移到 uv

Rye 已停止开发，本练习只训练阅读旧配置和迁移，不用 Rye 创建新项目。

## 对照文件

- `legacy-pyproject.toml`：旧项目中的 Rye 私有配置。
- `migrated-pyproject.toml`：迁移后尽量使用标准字段和 uv 工作流。

## 迁移任务

1. 记录原项目 Python 范围、运行依赖、开发依赖和脚本。
2. 安装 uv 后在副本中运行 `uv init`，不要直接破坏唯一工作副本。
3. 把运行依赖保留在 `[project].dependencies`。
4. 把只服务开发的依赖迁移到 `[dependency-groups].dev`。
5. 删除 `[tool.rye]`，使用 `uv lock` 和 `uv sync` 生成新锁定结果。
6. 把 Rye 脚本迁移为标准 CLI entry point、Nox session 或文档命令。
7. 在迁移前后分别运行测试、构建 wheel，并比较安装后的公开行为。

迁移的成功标准不是“新命令能运行”，而是依赖边界、测试、CLI 和构建产物行为
保持一致。
