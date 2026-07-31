# Python Learning Lab

一个可以直接运行、修改和测试的中文 Python 学习项目。课程不是孤立地罗列语法，而是通过小函数、小程序和测试理解 Python 为什么这样设计。

## 学习目标

- 掌握变量、容器、控制流、函数和模块
- 理解类、继承、组合、协议和数据类
- 掌握异常、上下文管理器、迭代器、生成器和异步编程
- 熟悉 `pathlib`、`collections`、`itertools`、`functools` 等标准库
- 系统学习 Pydantic 2：模型、约束、嵌套、校验器、序列化、错误和 Settings
- 学会用类型标注和 pytest 验证程序行为

## 环境准备

需要 Python 3.11 或更高版本：

```bash
git clone https://github.com/mono-kit/python-learning-lab.git
cd python-learning-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

运行课程演示：

```bash
python -m python_learning_lab
python -m python_learning_lab.pydantic_lab.main
```

运行测试：

```bash
pytest
```

## 课程地图

| 顺序 | 文件 | 内容 |
|---|---|---|
| 1 | `basics.py` | 变量、类型、条件、循环、推导式、模式匹配 |
| 2 | `collections_demo.py` | list、tuple、dict、set 及常用操作 |
| 3 | `functions.py` | 参数、返回值、闭包、装饰器、高阶函数 |
| 4 | `oop.py` | 类、继承、组合、property、dataclass、Protocol |
| 5 | `errors.py` | 异常、自定义异常、上下文管理器 |
| 6 | `iterators.py` | 可迭代对象、迭代器、生成器、`yield from` |
| 7 | `async_demo.py` | 协程、`await`、任务并发、TaskGroup |
| 8 | `stdlib_demo.py` | 常用标准库 |
| 9 | `pydantic_lab/` | 完整 Pydantic 专题 |

推荐学习方法：先运行一个文件；逐行阅读；修改输入预测结果；完成对应练习；最后运行测试。

## 目录结构

```text
src/python_learning_lab/    可运行的讲解代码
exercises/                  留有 TODO 的练习
solutions/                  参考答案
tests/                      用 pytest 描述正确行为
docs/                       学习路线和 Pydantic 讲义
```

更多顺序说明见 [`docs/roadmap.md`](docs/roadmap.md)，阶段复习见
[`docs/review.md`](docs/review.md)，Pydantic 专题见
[`docs/pydantic.md`](docs/pydantic.md)。
