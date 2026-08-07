# Python Learning Lab 协作规则

## 确认学习进度

- 用户说“继续学习”“下一课”或询问进度时，先读取根目录 `course.toml`。
- 只能以 `[progress].next_chapter` 作为下一课；不要根据最近新增的文件、聊天记忆或
  课程总章数猜测。
- 再读取该章节在 `[[chapters]]` 中声明的 `courseware`、`example`、`exercise`、`test`、
  `solution` 和 `command`，确认文件真实存在后再开始教学。
- `reviews/` 只记录已经完成章节的快速复习；完整课件始终读取本章目录中的
  `lesson.md`，进度数值仍以 `course.toml` 为准。

## 开始新章节教学

- 不要假设用户仍记得前面章节的知识，也不要假设用户已经熟悉本章示例、被测试代码或
  工程背景。
- 正式布置练习前，先重新讲解本章会用到的旧知识点，再逐个介绍本章源码中的主要类型、
  函数、对象关系和执行过程；说明哪些是 Python 语法、标准库能力、第三方库能力和本仓库
  自定义工具。
- 第一次引用一段现有实现时，先带用户阅读该实现及其公开接口，不能只给出测试任务并让
  用户自行反查源码。
- 每次只推进一个清晰的小主题，在确认用户理解当前模型后再进入下一组练习。

## 完成一章

- 只有用户明确表示学完，并且本章验收测试通过后，才把
  `[progress].completed_through` 更新为本章，把 `next_chapter` 更新为下一章。
- 在 `reviews/` 新增或更新本章独立总结，并更新 `reviews/README.md` 的当前进度；
  `tests/test_course_structure.py` 必须继续通过。
- 未学习章节的 TODO 不进入普通 `pytest`，只运行当前章节在清单中声明的命令。
- 已完成章节的练习不得继续保留 TODO 或 `NotImplementedError`；完成后的 `exercise.py`
  可以直接作为该章参考实现，避免维护重复答案。

## 新增或修改课程

- 普通章节必须使用 `lessons/NN_slug/` 独立目录，同时提供 `lesson.md`、练习、章节测试、
  示例源码、参考实现和准确运行命令。课件、练习和测试不得重新散落到共享目录。
- 所有课程代码都必须位于 `lessons/`。本章专用代码放回章节目录；确实被多个工程章节
  复用的实现才可放在 `lessons/_shared/`，并由 `course.toml` 显式登记，禁止复制多份。
- 每章 `lesson.md` 必须包含唯一的 `<!-- course-chapter: N -->` 标记，并具备足量正文与
  代码示例；课程总览中的几段提纲不能代替课件，也不允许多章共享一个课件文件。
- 已完成章节的 review 必须位于 `reviews/NN_slug.md`，包含唯一
  `<!-- review-chapter: N -->` 标记、易错点和快速自测；未完成章节不得提前创建 review。
- 测试编写型或实验型章节可以采用不同文件布局，但必须在 `course.toml` 中显式登记
  `kind` 和验收入口。
- 综合项目可以不提供完整参考答案，但必须声明 `solution_policy` 并提供分阶段验收。
- 新增章节时保持编号连续，并同步 `course.toml`、`lessons/README.md` 和 README。
- 修改练习、测试或答案后，运行 Nox `solution-tests`，确认同一套学习测试也能验证参考
  答案。
- 修改打包范围后运行 Nox `build` 与 `package_smoke`；sdist 应包含课程资产，wheel 只
  包含运行时包及声明的包内资源。
