# 学习路线

## 第一阶段：读懂表达式

阅读 `basics.py` 和 `collections_demo.py`。重点不是背关键字，而是理解一个表达式如何产生值，以及变量如何引用对象。

完成后应能解释：

- `==` 和 `is` 的区别
- 可变对象与不可变对象
- 切片、解包和推导式
- 真值判断与短路求值

## 第二阶段：组织代码

阅读 `functions.py`、`oop.py` 和 `errors.py`。

完成后应能解释：

- 位置参数、关键字参数、`*args`、`**kwargs`
- 闭包和装饰器为什么能工作
- 继承与组合的差别
- 上下文管理器如何保证资源被释放

## 第三阶段：控制执行过程

阅读 `iterators.py` 和 `async_demo.py`。

完成后应能解释：

- iterable、iterator 和 generator 的区别
- `yield` 如何暂停并恢复函数
- 协程为什么不是线程
- 并发任务如何被事件循环调度

## 第四阶段：数据边界

阅读 `docs/pydantic.md` 和 `pydantic_lab/`。

完成后应能把外部 JSON、环境变量或表单数据安全地转换成程序内部对象，并能向用户解释所有校验错误。

## 第五阶段：测试驱动练习

先阅读测试，再实现 `exercises/` 中的 TODO。测试是可执行的需求说明，不只是项目完成后的检查工具。

## 第六阶段：深入语言与工程实践

完成基础课程后，进入 [`advanced-roadmap.md`](advanced-roadmap.md)。这一阶段从
Python 数据模型、描述器、MRO 和高级类型标注出发，继续学习流式处理、
并发控制、测试分层、模块与导入系统、打包与发布、uv、Nox 和工具生态、
应用架构、SQLite、性能诊断，并最终完成一个本地任务队列综合项目。打包专题详见
[`packaging.md`](packaging.md)。

## 第七阶段：HTTP 与 ASGI 网络编程

完成 [`http-and-asgi.md`](http-and-asgi.md) 的第 21～26 章。从 HTTP 消息和标准库
客户端/服务端开始，再学习同步与异步客户端、timeout、重试和流式传输，最后手写
ASGI 应用并用 FastAPI/Uvicorn 把已有任务服务暴露为 HTTP API。

完成后应能解释：

- HTTP status failure 与 transport failure 为什么不是一回事
- 连接池、timeout、并发上限、流式响应和客户端生命周期
- ASGI 的 `scope`、`receive`、`send` 与事件顺序
- server、framework、application 和 middleware 的职责边界
