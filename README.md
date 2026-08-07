# Python Learning Lab

一个可运行、可修改、可测试的中文 Python 课程仓库。课程从基础语法逐步进入数据模型、
描述器、类型系统、异步并发、测试、打包、架构、SQLite、性能、HTTP 与 ASGI。

## 从哪里开始

[`course.toml`](course.toml) 是章节编号和学习进度的唯一清单。开始或继续学习时先读取：

```toml
[progress]
completed_through = 14
next_chapter = 15
reviews = "reviews"
```

- [`lessons/`](lessons/README.md)：1～26 章的课件、示例、练习、参考实现和章节测试。
- [`reviews/`](reviews/README.md)：只保存已经学完章节的快速复习总结。

## 统一章节结构

每一章都有自己的目录，不再跨目录寻找讲义、练习和验收：

```text
lessons/
├── 01_basics/
│   ├── lesson.md
│   ├── example.py
│   ├── exercise.py
│   └── test_lesson.py
├── 15_testing/
│   ├── lesson.md
│   ├── exercise.md
│   └── test_lesson.py
└── 20_task_queue/
    ├── lesson.md
    ├── exercise.md
    └── tests/
```

普通章节由三个固定部分组成：

1. `lesson.md`：从头学习所需的完整课件。
2. `exercise.py` 或 `exercise.md`：本章需要独立完成的任务。
3. `test_lesson.py` 或 `tests/`：可执行验收标准。

本章专用的示例与参考实现也放在同一目录。多个工程章节共同演进的任务队列代码位于
`lessons/_shared/`，避免复制实现。参考实现的准确位置记录在 `course.toml`；已经完成的
章节直接以完成后的 `exercise.py` 作为答案，不再额外保存重复副本。

第 15 章的产物本身就是 pytest 测试，因此使用练习说明加待完成测试；第 20 章是综合
项目，使用多个分阶段测试。两种例外都在 `course.toml` 中明确登记。

### 课程维护不变量

- 课程代码只进入 `lessons/`；根目录不再维护平行的 `src/`、`exercises/` 或
  `solutions/` 副本。
- 已完成章节的练习必须是真正完成态，不能继续包含 TODO 或 `NotImplementedError`。
- 练习测试与参考实现测试使用同一套断言，避免题目、验收和答案逐渐失配。
- sdist 保存完整课程资产；wheel 只包含第 16 章用于演示打包的最小运行时包和声明资源。

这些规则由 `tests/test_course_structure.py`、Nox `solution-tests`、`build` 和
`package_smoke` 持续验证。

## Review 的职责

`reviews/` 不承担首次教学，只用于学完后的快速恢复：

```text
reviews/14_concurrency.md
├── 一分钟速记
├── 易错点
└── 快速自测
```

只有用户明确学完、章节验收通过后才创建对应 Review，并同步更新课程进度。未完成章节
不会提前生成总结，避免把提纲误当课件。

## 环境准备

需要 Python 3.11 或更高版本：

```bash
git clone https://github.com/mono-kit/python-learning-lab.git
cd python-learning-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,web]'
```

也可以使用 uv：

```bash
uv sync --extra dev --extra web
```

## 学习一章

以当前第 15 章为例：

```bash
# 1. 阅读完整课件
less lessons/15_testing/lesson.md

# 2. 阅读练习要求并完成 TODO
less lessons/15_testing/exercise.md

# 3. 只运行本章验收
uv run pytest lessons/15_testing/test_lesson.py
```

每章的准确命令都记录在 `course.toml`。不要一次运行全部未完成练习；根目录普通
`pytest` 只收集 `tests/`，不会让后续章节的 TODO 干扰当前进度。

## 工程验证

```bash
uv run pytest
uvx nox -s lint typing tests-3.11
uvx nox -s solution-tests
uvx nox -s build package_smoke
```

Nox 的发布检查只构建和验证产物，不会上传到 PyPI。

## 仓库结构

```text
AGENTS.md                   跨会话学习与课程维护规则
course.toml                 章节、进度和每章资产的唯一清单
lessons/                    按章节组织的全部课程内容与代码
reviews/                    已完成章节的独立快速复习
tests/                      仓库自身的回归与结构门禁
```

完整课程索引见 [`lessons/README.md`](lessons/README.md)。
