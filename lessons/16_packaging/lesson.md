<!-- course-chapter: 16 -->

# 第 16 章：模块、打包、发布与工具

## 学习目标

完成本专题后，应能回答以下问题：

- 一个 `.py` 文件何时是脚本，何时是模块？
- import package、distribution package 和项目目录有什么区别？
- `import` 怎样查找、创建并缓存模块对象？
- `pyproject.toml` 中 `[build-system]`、`[project]` 和 `[tool.*]` 各负责什么？
- 构建前端与构建后端为什么要分开？
- sdist 和 wheel 分别给谁使用？
- 怎样在干净环境验证产物，而不是只验证源码目录？
- 怎样先发布到 TestPyPI，再安全地发布到 PyPI？
- pip、venv、build、twine、uv、Rye、Hatch、PDM 和 Poetry 的职责有什么不同？

课程遵循一个原则：

> 先理解 Python Packaging 标准和产物流，再学习工具的快捷命令。

工具会变化，标准和职责边界更持久。

## 1. 先统一术语

### 脚本

直接作为程序入口执行的 Python 文件：

```bash
python path/to/report.py
```

此时文件通常满足：

```python
__name__ == "__main__"
```

### 模块

能够被 Python 导入的代码单元，通常对应一个 `.py` 文件：

```python
import report
```

导入成功后，`report` 是模块对象，不只是文件名。

### import package

可以包含子模块的导入包：

```text
python_learning_lab/
├── __init__.py
├── errors.py
└── pydantic_lab/
    ├── __init__.py
    └── models.py
```

常规包通常包含 `__init__.py`。namespace package 可以没有该文件，并允许
同一个导入包分布在多个目录中。

### distribution package

由安装工具安装、由包索引分发的项目产物，例如：

```text
pydantic-2.x.y-py3-none-any.whl
```

distribution 名称与 import 名称不一定相同，也不保证一一对应。例如一个
distribution 可以提供多个 import package。

### 项目

包含源码、测试、文档、元数据和构建配置的开发目录：

```text
python-learning-lab/
├── pyproject.toml
├── src/
├── tests/
├── lessons/
├── reviews/
└── README.md
```

因此，“项目”“distribution package”“import package”“模块”不能混用。

## 2. 模块和导入系统

仓库内示例目录：`example_project/src/python_learning_lab/advanced/imports_lab/`

### 2.1 模块对象

第一次导入时重点观察：

```python
module.__name__
module.__package__
module.__file__
module.__spec__
```

模块顶层代码在第一次成功导入时执行。导入完成后，模块对象通常保存在：

```python
sys.modules
```

再次导入通常复用缓存，不会重新执行全部顶层代码。

### 2.2 查找路径

观察：

```python
sys.path
importlib.util.find_spec("python_learning_lab")
```

需要区分：

- 当前工作目录
- 可编辑安装后的包位置
- 虚拟环境的 `site-packages`
- 标准库路径
- 用户手动修改 `PYTHONPATH` 带来的隐式依赖

课程不把修改 `sys.path` 当作正常项目结构的解决方案。

### 2.3 绝对导入和相对导入

```python
from python_learning_lab.advanced.imports_lab import module_facts
from .inspection import welcome_text
```

需要掌握：

- 相对导入依赖当前模块的包上下文。
- 直接执行包内部文件可能破坏相对导入。
- `python -m package.module` 会按照模块方式建立正确包上下文。

### 2.4 包初始化和公开接口

理解：

```python
package/__init__.py
package/__main__.py
__all__
```

- `__init__.py` 可以组织包级公开接口，但不应放置昂贵或有副作用的初始化。
- `__main__.py` 让包支持 `python -m package`。
- `__all__` 主要控制 `from package import *`，不是访问控制或安全边界。

### 2.5 循环导入

构造并分析：

```text
models.py → services.py → models.py
```

不要只用“把 import 移进函数”掩盖设计问题。课程要求识别更深层原因：

- 两个模块职责没有分开。
- 共享类型放错层级。
- 包级 `__init__.py` 重新导出过多内容。
- 运行时只需要类型却执行了真实导入。

练习使用职责拆分、Protocol 或 `TYPE_CHECKING` 消除循环。

### 2.6 包内资源和已安装元数据

不要依赖相对于当前工作目录的脆弱路径：

```python
from importlib.resources import files

template = files("package.templates").joinpath("report.txt")
```

读取已安装 distribution 的版本与入口点：

```python
from importlib.metadata import version

version("python-learning-lab")
```

### 模块练习

1. 写一个模块，在顶层打印初始化信息，证明缓存行为。
2. 用 `python file.py` 和 `python -m package.module` 对比 `__package__`。
3. 制造并修复一个循环导入。
4. 把模板文件放入包内，并在 wheel 安装后通过 `importlib.resources` 读取。

### 第一阶段复盘：导入观察器

本阶段完成 `exercise.py` 中的四个边界函数，建立模块、import package 和已安装
distribution 之间的连接。

#### 从 import 语句到模块对象

模块是运行时对象，不只是一个 `.py` 文件。解释器执行 import 时，先检查完整模块名是否
已存在于 `sys.modules`；未命中时才查找 spec、创建模块对象并执行顶层代码，成功后继续
复用该对象：

```text
import 语句
  → sys.modules 缓存
  → 查找 ModuleSpec
  → 创建 module 对象
  → 执行模块顶层代码
  → 在当前作用域绑定名称
```

动态模块名必须使用标准库函数：

```python
from importlib import import_module

module = import_module("python_learning_lab.advanced.imports_lab")
```

`module.__name__` 是完整模块名，`module.__package__` 是相对导入所需的包上下文；
`module.__file__` 可能不存在，`module.__spec__` 也可能是 `None`，因此通用观察代码需要
显式处理这些边界：

```python
spec = module.__spec__
facts = {
    "__file__": getattr(module, "__file__", None),
    "spec_name": spec.name if spec is not None else None,
    "origin": spec.origin if spec is not None else None,
}
```

连续两次 `import_module(name)` 后使用 `first is second`，可以证明正常重复导入复用了同一
对象；它不表示模块永远不会重跑，因为 `importlib.reload()` 或删除缓存会改变这一条件。

#### 可复用函数与手动观察入口

函数契约要求返回字典时，只打印而没有 `return` 会隐式返回 `None`。可复用函数负责收集
数据，直接运行文件时的展示逻辑放在入口保护中：

```python
if __name__ == "__main__":
    for key, value in module_facts("json").items():
        print(f"{key}: {value}")
```

直接执行文件时 `__name__ == "__main__"`；测试通过 `runpy.run_path()` 加载练习时不满足
该条件，因此不会产生手动展示输出。

#### 包内资源不依赖当前工作目录

`Path("resources/welcome.txt")` 相对于 `Path.cwd()`，程序从其他目录启动或安装 wheel 后
就可能失效。`importlib.resources.files()` 先通过 import 系统定位 package，再返回实现
`Traversable` 协议的资源根：

```python
from importlib.resources import files

resource = files(package).joinpath(relative_path)
text = resource.read_text(encoding="utf-8").strip()
```

`read_text()` 已经完成打开、读取和关闭并直接返回 `str`，不能再把结果放进 `with`。
需要上下文管理器时应调用 `resource.open(...)`；`open_text` 不是资源对象的方法。

#### distribution 元数据不是模块变量

版本是 distribution 的标准安装元数据。源码中的 `package.__version__` 只是可选约定，
可能不存在或与实际安装产物漂移；应使用 distribution 名称查询当前环境：

```python
from importlib.metadata import version

installed_version = version("python-learning-lab")
```

这里的 distribution 名称 `python-learning-lab` 与 import package 名称
`python_learning_lab` 属于不同命名空间，也不保证一一对应。找不到已安装 distribution
时，`version()` 会抛出 `PackageNotFoundError`。

#### 第一阶段快速自测

1. 为什么 `first is second` 比比较模块路径更能证明缓存复用？
2. `__name__` 与 `__package__` 分别描述什么？
3. 为什么读取通用模块信息时要防守 `__file__` 和 `__spec__` 缺失？
4. `read_text()` 与 `open()` 的返回对象和资源管理方式有什么区别？
5. 为什么包内资源不能依赖 `Path.cwd()`？
6. 为什么查询安装版本要传 distribution 名称，而不是 import package 名称？

本阶段测试通过只表示导入观察器练习完成。第 16 章的下一阶段是项目布局与可运行包；整章
仍未完成，因此不创建第 16 章 review，也不推进 `course.toml` 中的正式进度。

## 3. 项目布局

### 脚本项目、应用和库

```text
一次性脚本
→ 通常不需要构建为 distribution

可安装 CLI 或服务应用
→ 需要包、入口点和可重复环境

供其他项目导入的库
→ 需要稳定公共 API、兼容范围和发布产物
```

### `src/` 布局

当前项目使用：

```text
src/python_learning_lab/
```

它能减少“源码目录恰好在 import 路径上”造成的假成功，促使测试使用真正
安装后的包。

### 命令行入口

标准入口声明放在：

```toml
[project.scripts]
python-learning-lab = "python_learning_lab.__main__:main"
```

安装后应能直接运行：

```bash
python-learning-lab
```

入口函数应该返回清楚的退出码，并把解析参数、调用服务和展示结果分开。

## 4. `pyproject.toml`

现代项目应重点理解三个区域。

### `[build-system]`

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"
```

它声明构建所需依赖和构建后端。构建前端会在隔离环境安装这些依赖，再调用
后端完成构建。

### `[project]`

```toml
[project]
name = "python-learning-lab"
version = "0.1.0"
description = "..."
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["pydantic>=2,<3"]
```

课程覆盖：

- distribution 名称与版本
- Python 版本范围
- 运行时依赖
- 作者、维护者、许可证和项目 URL
- 静态版本与动态版本
- CLI scripts 和通用 entry points

### 可选依赖与依赖组

提供给包使用者选择的功能依赖：

```toml
[project.optional-dependencies]
email = ["email-validator"]
```

只服务当前项目开发流程、不会成为发布元数据的依赖组：

```toml
[dependency-groups]
dev = ["pytest", "ruff"]
```

必须理解 extras 和 dependency groups 的服务对象不同。

### `[tool.*]`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

它保存具体工具自己的配置，不属于项目核心发布元数据。

## 5. 构建架构

### 构建前端

前端负责建立构建环境并调用标准接口，例如：

```bash
python -m build
uv build
```

### 构建后端

后端读取项目配置并决定产物内容，例如：

- setuptools
- Hatchling
- flit-core
- pdm-backend
- poetry-core
- uv-build
- Maturin（常用于 Rust 扩展）
- scikit-build-core（常用于 CMake/C/C++ 扩展）

不能把 `uv build` 当成“uv 自动决定所有打包规则”。uv 在此是前端，实际
文件选择、元数据和构建细节由 `[build-system]` 指定的后端负责。

### 构建隔离

标准构建默认在隔离环境安装 `[build-system].requires`。这可以发现没有声明
的隐式构建依赖，提高可重复性。

禁用隔离只能作为处理特殊项目的例外手段，不能作为默认解决方式。

## 6. sdist、wheel 与 editable install

### sdist

源代码分发通常是：

```text
project-name-version.tar.gz
```

它应包含足以从源码构建项目的文件。用户安装 sdist 时，通常需要在本地运行
构建后端。

本仓库本身是课程项目，因此源码包还必须包含 `course.toml`、讲义、练习、学习测试和
参考答案；这些开发/教学资产不应进入运行时 wheel。`MANIFEST.in` 负责声明 sdist 的
额外内容，Nox 的 build session 会检查关键课程文件没有遗漏。

### wheel

构建后的分发格式：

```text
project_name-version-py3-none-any.whl
```

wheel 本质上是带标准目录和元数据的 ZIP。安装通常只需把内容放到正确位置，
不必再次执行项目构建。

纯 Python 项目通常可以使用一个通用 wheel；包含二进制扩展的项目往往需要
为 Python ABI、操作系统和 CPU 架构分别构建 wheel。

### editable install

```bash
python -m pip install -e .
```

它适合开发：源码修改可以立即反映到环境中。但 editable install 成功并不能
证明最终 wheel 内容正确，所以发布前必须测试真实 wheel。

### 构建练习

```bash
python -m build
python -m twine check dist/*
python -m zipfile -l dist/*.whl
```

还要从 sdist 再构建 wheel，防止源码分发遗漏构建所需文件。

## 7. 在干净环境验证产物

不能只在源码目录运行测试。发布候选产物至少经过以下验证：

```text
清理旧 dist
→ 构建 sdist 和 wheel
→ 检查元数据和 README 渲染
→ 在全新虚拟环境安装 wheel
→ 从项目目录之外执行 import
→ 运行 CLI smoke test
→ 从 sdist 构建 wheel并重复验证
```

需要验证：

- 包内资源是否包含。
- 测试或开发文件是否意外进入 wheel。
- 运行依赖是否完整。
- 入口点是否生成。
- `importlib.metadata.version()` 是否正确。

### 第二阶段复盘：从项目配置到真实 wheel

本阶段不再只观察源码里的模块，而是沿着完整产物流回答三个问题：构建工具读取了什么、
sdist 和 wheel 为什么包含不同文件，以及安装后的程序是否真的能脱离源码目录运行。

#### 三种启动方式执行的代码不同

同一个 package 可以有三条常见启动路径：

```text
import python_learning_lab
→ 导入 package，执行 __init__.py
→ 不会因为存在 __main__.py 就自动执行它

python -m python_learning_lab
→ 先建立 package 上下文，再执行 package/__main__.py
→ 运行入口中的 __name__ 是 "__main__"

python-learning-lab
→ 安装工具根据 [project.scripts] 生成命令包装器
→ 包装器导入 python_learning_lab.__main__:main 并调用函数
```

直接执行包内的 `__main__.py` 文件不等价于 `python -m package`：前者缺少解释器根据完整
模块名建立的 `__package__` 和 `__spec__` 上下文，包内相对导入可能因此失败。

#### `pyproject.toml` 中每块配置各有所有者

当前项目的关键配置关系是：

```text
[build-system]
→ 构建前端要安装哪个后端、调用哪个标准构建接口

[project]
→ distribution 名称、版本、Python 范围、运行时依赖和入口点

[project.optional-dependencies]
→ 安装者可以选择的 extras；本项目的 dev 也是发布元数据中的一个 extra

[tool.setuptools.packages.find]
→ setuptools 从哪个 src 根目录发现 import package

[tool.setuptools.package-data]
→ 哪些非 Python 包内资源进入 wheel

[tool.pytest.*] / [tool.ruff] / [tool.mypy]
→ 各开发工具自己的行为，不负责决定 wheel 的包发现规则
```

因此，pytest 能从源码导入 package，只能证明测试路径配置有效；它不能证明 setuptools
找到了相同代码，更不能证明 wheel 包含所需文件。这正是 `src/` 布局要暴露的“源码目录
碰巧可导入”问题。

运行依赖与构建依赖也属于两个阶段：`[project].dependencies` 安装到使用者环境；
`[build-system].requires` 只用于隔离构建环境。一个纯 Python wheel 安装完成后，不需要为
了运行它而继续保留 setuptools。

#### 文件清单由构建配置产生，Nox 只负责验证

本仓库刻意让两个产物服务不同对象：

- `MANIFEST.in` 补充 sdist 的课程源码、讲义、练习、测试和工程配置。
- setuptools 的 package discovery 决定 wheel 中的 Python package。
- `package-data` 把 `resources/welcome.txt` 这类运行时资源加入 wheel。
- Nox 的 `build` 和 `package_smoke` session 检查结果，但不会反过来改变产物内容。

由此可以推导：若删除 `package-data` 声明，不能只看 `MANIFEST.in` 就断言 wheel 中一定
有或没有资源；setuptools 的 `include-package-data`、生成的文件清单和构建缓存也可能参与
选择，必须清理旧产物后重新审计。若只删除 Nox 的资源断言，构建内容不会改变，只是缺少
了发现错误的门禁。更换构建后端时也不能假设 setuptools 的配置继续生效，必须按照新
后端的规则重新声明并审计文件范围。

本次实际审计得到：wheel 只含最小运行时代码、distribution 元数据和声明的包内资源；
sdist 还含完整课程资产。这里 sdist 比 wheel 大，是本仓库内容策略造成的事实，不是
“sdist 永远更大”的格式规则。

纯 Python wheel 文件名中的标签：

```text
python_learning_lab-0.1.0-py3-none-any.whl
                             │    │    └─ 平台标签：任意平台
                             │    └────── ABI 标签：不绑定特定 Python ABI
                             └─────────── Python 标签：Python 3
```

其中 `none` 描述 ABI，不表示“没有依赖”或“不限制依赖版本”；依赖要求记录在 wheel 的
distribution 元数据中。

#### 干净安装验证的是产物，不是工作树

本阶段把构建出的真实 wheel 安装进全新虚拟环境，并从源码目录之外运行。结果证明：

- `python_learning_lab.__file__` 来自虚拟环境的 `site-packages`，不是仓库源码。
- `importlib.metadata.version("python-learning-lab")` 能读取 wheel 安装的版本元数据。
- `importlib.resources` 能读取 wheel 内的 `welcome.txt`。
- `python -m python_learning_lab` 和生成的 `python-learning-lab` 命令都能正常运行。
- 运行环境中找不到 setuptools，程序仍能工作，说明构建后端没有泄漏成运行时依赖。

这组结果才构成 wheel smoke test。editable install、在仓库根目录 import 成功，或者直接
检查源码文件，都不能替代它。

#### 第二阶段快速自测

1. 普通 `import package` 为什么不会自动运行 `package/__main__.py`？
2. `[project.scripts]` 左右两侧分别代表什么？
3. pytest 能导入源码，为什么不能证明 wheel 一定能导入？
4. sdist 和 wheel 的主要使用者与文件范围有什么差异？
5. wheel 标签 `py3-none-any` 的三个部分分别描述什么？
6. 为什么构建检查删除后，产物内容不会自动变化？
7. 为什么应从源码目录之外安装并验证 wheel？
8. 干净运行环境没有 setuptools，为什么程序仍然能够运行？

本阶段已经完成本地构建、产物审计和真实 wheel 的隔离安装验证；没有向任何包索引上传
文件。第 16 章接下来学习版本与发布策略，整章仍未完成，因此此时不创建第 16 章 review，
也不推进 `course.toml` 中的正式进度。

## 8. 版本与发布策略

### PEP 440 版本

课程覆盖：

```text
1.2.0       正式版本
1.2.0a1     alpha
1.2.0b1     beta
1.2.0rc1    release candidate
1.2.0.post1 发布后的修订
1.2.0.dev1  开发版本
```

依赖范围和项目发布版本都应遵守 Python 生态的版本规范，而不是只凭字符串
比较。

### 发布前检查单

1. 版本号是新版本，且元数据一致。
2. 测试、静态检查、格式检查和构建全部通过。
3. 变更记录和 README 已更新。
4. sdist 与 wheel 内容经过检查。
5. 在全新环境验证安装和 import。
6. 使用 TestPyPI 演练后再发布正式 PyPI。

### TestPyPI

TestPyPI 与正式 PyPI 是独立服务，适合练习完整发布流程：

```bash
python -m twine upload --repository testpypi dist/*
```

从 TestPyPI 安装时，需要留意依赖可能仍来自正式 PyPI；课程会明确配置主索引
和额外索引，避免误判。

### 正式发布

标准工具链：

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

uv 工具链：

```bash
uv build
uv publish
```

认证优先使用每项目 token 或包索引支持的 Trusted Publishing，避免在仓库或
命令历史中保存长期密码。

同一版本的已发布文件通常不能用不同内容覆盖。出现错误时应发布新版本，或在
合适场景下 yank 有问题的版本，而不是试图静默替换产物。

真正发布到公共索引属于外部写操作，练习默认停在本地构建和 TestPyPI；正式
发布前必须再次确认项目名、版本、许可证、产物和目标索引。

## 9. 工具角色地图

### 标准组合：venv + pip + build + twine

```text
venv   → 创建隔离环境
pip    → 安装 distribution
build  → 调用构建后端生成 sdist/wheel
twine  → 检查并上传产物
```

这套组合最适合学习职责边界，也是排查其他一体化工具问题时的基线。

### uv：本课程的主要现代工具

uv 可以覆盖：

```text
Python 版本管理
虚拟环境
依赖解析和锁定
环境同步
命令运行
工具隔离运行
workspace
构建
发布
```

核心命令学习顺序：

```bash
uv init
uv add / uv remove
uv lock / uv sync
uv run
uv tree
uvx
uv build
uv publish
```

需要同时理解：

- `pyproject.toml` 是声明，`uv.lock` 是具体解析结果。
- `uv sync` 让环境符合锁文件，`uv run` 在同步后的项目环境运行命令。
- 应用通常需要锁定完整环境；库仍应在发布元数据中声明合理兼容范围。
- `uv build` 可以调用 setuptools、Hatchling 等后端，也可以选择 uv-build。

### Rye：迁移案例，不作为新项目首选

Rye 官方已经停止开发，并建议迁移到同一维护团队的 uv。因此课程只保留：

- 阅读遗留项目中的 `[tool.rye]` 和 Rye 命令。
- 把依赖、脚本、Python 版本和锁定流程迁移到 uv。
- 比较迁移前后的行为是否一致。

不再为新练习创建 Rye 项目，也不把 Rye 作为长期工具推荐。

### 第三阶段复盘：版本约束、uv 状态链与 Rye 迁移

本阶段把“允许安装什么版本”“实际锁定并安装了什么”以及“由哪个工具执行工程任务”
连接起来，重点记录实际出现过的误区和当前仓库的特殊配置。

#### PEP 440 按数字组件比较版本

一个常见发布生命周期的顺序是：

```text
0.2.0.dev1
< 0.2.0a1
< 0.2.0b1
< 0.2.0rc1
< 0.2.0
< 0.2.0.post1
```

版本组件按数字值比较，而不是把整个版本当成字符串或小数。本阶段重点纠正：

```text
2.9.0  → (2, 9, 0)
2.10.0 → (2, 10, 0)

2 == 2，随后 10 > 9
所以 2.10.0 > 2.9.0
```

字符串比较可能得到相反结果，但依赖解析器使用版本语义。PEP 440 比较 release segment
时会补零，因此 `0.2` 与 `0.2.0` 等价。范围 `>=0.2,<0.3` 中的逗号是逻辑 `and`：

```text
0.2.0.dev1  < 0.2，不满足下界
0.2.0a1     < 0.2，不满足下界
0.2.0b1     < 0.2，不满足下界
0.2.0rc1    < 0.2，不满足下界
0.2.0       = 0.2，满足
0.2.0.post1 > 0.2 且 < 0.3，满足并且更新
0.3.0       不满足上界
```

因此最新匹配版本是 `0.2.0.post1`。下界只负责筛选候选，不能直接当成安装结果。

#### release 是版本，file 是该版本的产物

一次 `0.2.0` release 可以同时包含一个 sdist 和多个平台 wheel：

```text
project 0.2.0 release
├── project-0.2.0.tar.gz
├── project-0.2.0-py3-none-any.whl
├── project-0.2.0-cp313-...-macosx_....whl
└── project-0.2.0-cp313-...-manylinux_....whl
```

这是一次 release、多个 file。PyPI（以及独立的 TestPyPI）不允许用不同内容覆盖已经使用
过的文件名；即使删除文件，也不能把修复后的产物继续作为同名文件上传。漏资源等会改变
wheel 运行行为的问题，应选择新的正常版本、清理并重新构建，再执行 wheel smoke test；
不要默认用 `.postN` 代替正常修订版本。

有问题的已发布版本通常优先考虑 yank：普通解析会避开它，同时历史文件仍然存在；删除
则是破坏性且不可恢复的操作。

#### uv 管理声明、解析、环境和执行之间的状态链

uv 项目的核心状态流是：

```text
pyproject.toml
声明允许的依赖范围
    │ uv lock
    ▼
uv.lock
保存解析出的精确版本、来源、哈希和条件
    │ uv sync
    ▼
.venv
保存当前机器实际安装的环境
    │ uv run
    ▼
在项目环境中执行命令
```

四层不能混为一谈：锁文件里有某个包，不代表当前环境已经同步；环境里碰巧存在某个包，
也不代表项目声明了它。`uv lock` 负责解析和锁定，`uv sync` 负责把锁定结果落实到环境，
`uv run` 会在执行前检查项目状态并按需同步。

当前仓库的 `pytest` 位于 optional extra `dev`，所以从干净环境运行测试时必须显式选择：

```bash
uv run --extra dev pytest
uv run --locked --extra dev pytest  # CI：锁文件过期就失败
```

这是因为当前配置是：

```toml
[project.optional-dependencies]
dev = ["pytest>=8,<10", "ruff>=0.9"]
```

这里的 `dev` 是发布元数据中的 optional extra，仅仅因为名字叫 `dev` 并不会由普通
`uv sync` 自动选择。真正只服务仓库开发、并由 uv 默认同步的开发依赖应放在：

```toml
[dependency-groups]
dev = ["pytest>=8,<10", "ruff>=0.9"]
```

`--locked` 要求 `uv.lock` 与项目声明一致，过期就失败而不是自动改锁文件；`--frozen`
直接使用现有锁文件而不检查声明是否变化；`--no-sync` 跳过环境同步。三个开关解决不同
问题，不能都理解成“运行得更快”。

#### `uv run`、`uvx`、`uv add` 和 `uv build` 各有边界

需要当前项目和锁定依赖的测试使用：

```bash
uv run --extra dev pytest
uv run python-learning-lab
```

`uvx`（`uv tool run` 的简写）在独立工具环境运行 CLI，不保证安装当前项目。因此不能用
裸 `uvx pytest` 代替上面的项目测试。下面的命令只读取并列出 Nox session，不创建 session
环境：

```bash
uvx nox --list
```

真正运行时：

```bash
uvx nox -s package_smoke
```

uvx 只负责提供 Nox；Nox 此时才根据 `noxfile.py` 创建 session 环境并安装所需内容。

正式增加项目依赖时使用 `uv add`，让 `pyproject.toml`、`uv.lock` 和项目环境一起更新。
只在环境中执行 `uv pip install` 不会自动形成项目声明，之后的 exact sync 可能移除这种
未声明状态。

执行 `uv build` 也不意味着 uv 一定是构建后端。当前仓库的调用链是：

```text
uv build（构建前端）
→ setuptools.build_meta（pyproject.toml 指定的构建后端）
→ sdist / wheel
```

#### Rye 迁移的是行为，不是配置文本

Rye 已停止开发，遗留项目迁移到 uv 时应先分类旧配置：

```text
[project] 标准字段
→ 保留 Python 范围、运行依赖、名称和版本

[tool.rye] 中的 dev-dependencies
→ 迁入 [dependency-groups].dev

供安装者使用的产品命令
→ 迁入 [project.scripts] 的 module:function 入口点，并确保目标 callable 确实存在

test 等开发任务
→ uv run、Nox 或 CI；不要暴露成所有用户都会安装的 console script

Rye 锁文件
→ 不能只改名；根据标准依赖声明重新解析并生成 uv.lock
```

本章迁移示例还显式选择 Hatchling：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

此时 `uv build` 仍是前端，`hatchling.build` 才是后端。迁移验收应比较 Python 范围、运行
与开发依赖、测试、产品 CLI 和 wheel 的安装后行为，不能只以 `uv sync` 没报错为标准。

#### 第三阶段快速自测

1. 为什么 `2.10.0` 大于 `2.9.0`？
2. `>=0.2,<0.3` 在给定候选中为什么会选择 `0.2.0.post1`？
3. 一次 release 和它包含的 sdist/wheel 文件是什么关系？
4. 为什么已经上传的错误 wheel 不能用相同版本覆盖？
5. `uv lock`、`uv sync` 与 `uv run` 分别改变或使用哪一层状态？
6. 当前仓库为什么必须使用 `--extra dev` 才能从干净环境运行 pytest？
7. 测试当前 `src/` 项目时，为什么应使用 `uv run --extra dev pytest` 而不是 `uvx pytest`？
8. Rye 的产品 CLI 与开发任务为什么不能机械地一起迁入 `[project.scripts]`？

本阶段没有上传任何产物；TestPyPI/正式发布认证教学和 uv 的 dry-run 依赖图实验均已
跳过。Rye 配置映射已经讲解，但理解题尚未验收，也没有进行迁移实操；下次从 Rye 的迁移
边界继续，而不是直接进入 Nox。第 16 章仍未完成，因此不创建第 16 章 review，也不推进
`course.toml` 中的正式进度。

### 其他项目管理工具

| 工具 | 课程中的定位 |
|---|---|
| Poetry | 一体化项目、依赖、构建和发布工作流；学习互操作边界 |
| PDM | 标准导向的项目管理与依赖工作流；了解其后端和锁文件 |
| Hatch | 环境矩阵、版本和发布工作流；Hatchling 是独立构建后端 |
| Nox | 用 Python 编写可重复的隔离任务与多版本测试矩阵 |
| pip-tools | 从输入依赖编译可重复 requirements 文件 |
| pipx | 在隔离环境安装和运行 Python CLI 工具 |

目标不是把每个工具都熟练背一遍，而是看到项目后能判断：

```text
谁管理 Python？
谁解析并锁依赖？
谁创建环境？
谁是构建前端？
谁是构建后端？
谁上传产物？
哪些文件属于标准，哪些是工具私有格式？
```

## 10. Nox：可重复任务与环境矩阵

Nox 使用项目根目录的 `noxfile.py` 定义 session。每个 session 表示：

```text
一个隔离环境
+
需要安装的依赖
+
需要按顺序执行的命令
```

Nox 的职责是编排和隔离工程任务。它不是依赖解析器、构建后端或包索引上传
协议，不能取代对 uv、build backend 和发布流程的理解。

### Nox 与 uv 的配合

课程使用 uv 作为优先虚拟环境后端，并在 uv 不可用时回退到 virtualenv：

```python
import nox

nox.options.default_venv_backend = "uv|virtualenv"
```

也可以不把 Nox 永久安装进当前项目环境，而是通过隔离工具运行：

```bash
uvx nox --list
uvx nox
uvx nox -s tests
```

职责关系：

```text
uv
→ Python、环境、依赖解析、锁文件、安装、构建和发布

Nox
→ 把测试、检查、构建和产物验证组织成可重复 session
→ 在多个 Python 版本和参数组合中运行这些 session
```

### 基础 `noxfile.py`

```python
from pathlib import Path

import nox


nox.options.default_venv_backend = "uv|virtualenv"
nox.options.sessions = ["lint", "typing", "tests", "build"]


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session
def typing(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.install("mypy")
    session.run("mypy", "src", "tests")


@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session: nox.Session) -> None:
    session.install("-e", ".[dev]")
    session.run("pytest", *session.posargs)


@nox.session
def build(session: nox.Session) -> None:
    session.install("build", "twine")
    session.run("python", "-m", "build")
    artifacts = [str(path) for path in Path("dist").iterdir()]
    session.run("twine", "check", *artifacts)
```

命令：

```bash
nox --list
nox -s tests
nox -s tests-3.11
nox -s lint typing
nox -s tests -- -k pydantic -x
```

`session.posargs` 把 `--` 后面的参数传给 session 内部命令，因此开发者不需要
为每一种 pytest 过滤条件新增 session。

### 多 Python 版本

```python
@nox.session(python=["3.11", "3.12", "3.13", "3.14"])
def tests(session):
    ...
```

Nox 会为每个解释器建立独立 session。课程后期应从项目声明的支持版本生成
矩阵，而不是让 `requires-python`、分类信息和 Nox 列表长期不一致。

Nox 官方的 `nox.project` 辅助函数可以读取：

- `pyproject.toml`
- `[dependency-groups]`
- 声明的 Python 版本信息

### session 参数化

除了 Python 版本，还可以测试不同依赖版本或配置：

```python
@nox.session
@nox.parametrize("constraint", ["pydantic==2.7.*", "pydantic<3"])
def compatibility(session, constraint):
    session.install(constraint)
    session.install("-e", ".[dev]")
    session.run("pytest", "lessons/09_pydantic/test_lesson.py")
```

这种矩阵只应用于真正承诺支持的组合，不能无目的地把所有版本相乘。

### 构建与产物 smoke test

课程最终应具有以下 sessions：

```text
tests
→ 多 Python 版本运行测试

lint
→ Ruff 规则和格式检查

typing
→ 静态类型检查

solution-tests
→ 用章节学习测试验证参考答案，并单独运行第 15 章参考测试

build
→ 构建 sdist/wheel，运行 twine check，并确认 sdist 含完整课程资产

package_smoke
→ 在全新 session 安装 wheel，从源码目录外验证 import 和 CLI

release_check
→ 编排测试、检查、构建和产物验证，但不自动发布
```

`solution-tests` 通过 `PYTHON_LEARNING_LAB_TARGET=solution` 让同一组章节测试加载
`course.toml` 声明的 `solution`；普通学习命令不设置该变量，始终加载各章的
`exercise.py`。综合项目没有答案，
因此该 session 明确忽略 `lessons/20_task_queue/tests/`，第 15 章则直接运行其参考测试文件。

`release_check` 只负责证明发布候选物满足条件。真正的 `uv publish` 或
`twine upload` 仍应是需要明确目标索引和授权的独立步骤。

### 环境复用

Nox 默认强调隔离和可重复性。开发时可以复用 session 环境提高速度：

```bash
nox --reuse-venv=yes -s tests
```

但复用环境可能隐藏依赖声明遗漏。正式发布检查必须至少有一次使用新环境完成。

### Nox 练习

1. 新增 `tests` session，并通过 `session.posargs` 运行单个测试。
2. 参数化项目支持的多个 Python 版本。
3. 使用 `uv|virtualenv` 后端，分别验证 uv 存在和缺失时的行为。
4. 新增 `solution-tests`，防止练习、测试和参考答案漂移。
5. 新增 `build` 与 `package_smoke`，确保测试的是真实 wheel。
6. 新增 `release_check`，失败时不允许继续到发布步骤。
7. 比较 Nox session 与手写 shell 命令在跨平台、隔离和可读性上的差异。

### Nox 完成标准

- `nox --list` 能清楚展示每个工程任务。
- 开发者可以只运行一个 session，也可以运行默认质量门禁。
- 测试矩阵覆盖项目声明支持的 Python 版本。
- uv 是优先后端，但 Nox 配置不把 uv 当成构建后端或上传协议。
- wheel smoke test 在隔离环境和项目目录之外运行。
- 发布 session 不在没有明确授权时上传公共包。

## 11. 构建后端选择实验

在一次性示例项目中分别尝试：

### setuptools

- 当前项目已经使用。
- 生态成熟，配置能力广。
- 适合作为兼容性和传统项目基线。

### Hatchling

- 专注现代 Python 构建后端。
- 适合纯 Python 包和 Hatch 生态。

### flit-core

- 强调简单纯 Python 包。
- 适合元数据与源码关系直接的项目。

### uv-build

- 与 uv 项目工作流集成紧密。
- 适合对其约束模型匹配的新纯 Python 项目。

### Maturin / scikit-build-core

- 只做概念和最小实验。
- 前者用于 Rust 扩展，后者用于 CMake/C/C++ 扩展。
- 不在掌握纯 Python 发布前进入原生扩展细节。

实验要求同一简单包使用不同后端构建，然后比较：

- `pyproject.toml`
- sdist 文件清单
- wheel 文件清单
- editable install
- 动态版本和包内资源支持
- 构建时间与错误可读性

## 12. 练习项目

建议单独创建不与正式包名冲突的练习 distribution。

### 练习一：导入观察器

输出模块的 `__name__`、`__package__`、`__spec__`，观察脚本运行、`-m` 运行和
安装后运行的差别。

### 练习二：可安装 CLI

创建 `src/` 布局、包内资源和 `[project.scripts]`，构建后在干净环境执行。

### 练习三：产物审计

自动检查 sdist 与 wheel 的文件清单、元数据、许可证、资源和依赖。

### 练习四：TestPyPI 发布演练

使用唯一项目名发布测试版本，随后从项目目录外安装并运行。

### 练习五：uv 工作流

用 uv 管理 Python、锁文件、依赖组、测试、构建和 TestPyPI 发布，证明产物与
标准 build 前端构建的行为一致。

### 练习六：Rye 迁移

给定一个小型遗留 Rye 项目，迁移到 uv，并用测试和构建产物对比证明行为没有
改变。

### 练习七：Nox 工程门禁

用 Nox 编排多版本测试、参考答案验收、Ruff、类型检查、构建、twine 检查、sdist 课程
资产检查和 wheel smoke test；再用 uv 作为 session 后端运行同一套流程。

## 13. 本仓库的实施顺序

1. 保留当前 setuptools 后端，先学习标准和基线命令。
2. 新增 CLI entry point 与包内资源，理解模块和安装行为。
3. 使用 `python -m build` 构建并审计 sdist/wheel。
4. 在临时虚拟环境安装 wheel 并运行 smoke test。
5. 引入 uv 管理依赖、锁文件、运行、构建与工具。
6. 新增 Nox sessions，统一测试、参考答案验收、检查、构建和 wheel smoke test。
7. 在独立示例包比较 Hatchling、flit-core 和 uv-build，不立即迁移主项目。
8. 使用 TestPyPI 做发布演练。
9. 最后设计正式版本、发布检查单和安全发布流程。

## 14. 完成标准

- 能准确区分模块、import package、distribution package 和项目。
- 能解释 `sys.path`、`sys.modules`、相对导入和 `python -m`。
- 能独立编写 `[build-system]`、`[project]` 和 `[project.scripts]`。
- 能区分前端、后端、安装器、解析器、锁文件和上传工具。
- 能构建并检查 sdist 与 wheel。
- 能在干净环境验证安装、导入、资源和 CLI。
- 能使用标准工具链和 uv 完成同一构建流程。
- 能用 Nox 在隔离环境编排多版本测试与发布前检查。
- 知道 Rye 是遗留迁移知识，而不是新项目默认选择。
- 能在 TestPyPI 演练，并清楚正式发布的不可逆影响。
- 遇到陌生工具时，能按职责判断它与 Python 标准的关系。

## 官方参考

- [Python Packaging User Guide：Packaging Flow](https://packaging.python.org/en/latest/flow/)
- [Python Packaging User Guide：pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python Packaging User Guide：Packaging Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Python Packaging User Guide：TestPyPI](https://packaging.python.org/en/latest/guides/using-testpypi/)
- [uv：项目工作流](https://docs.astral.sh/uv/concepts/projects/)
- [uv：构建和发布](https://docs.astral.sh/uv/guides/package/)
- [Rye：迁移到 uv](https://rye.astral.sh/guide/uv/)
- [Nox：官方教程](https://nox.thea.codes/en/stable/tutorial.html)
- [Nox：配置与 API](https://nox.thea.codes/en/stable/config.html)
