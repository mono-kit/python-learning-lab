<!-- review-chapter: 12 -->

# 第 12 章快速复习：高级类型标注

## 一分钟速记

- 标注主要服务静态检查，通常不自动阻止运行时调用。
- `Any` 关闭局部检查；`object` 接受所有对象但只允许通用安全操作。
- `TypeVar` 保存输入、存储和输出之间的类型关系。
- `Protocol` 按方法能力匹配，无需显式继承。
- `TypedDict` 描述 dict 的静态形状，不创建运行时校验模型。
- `TypeGuard` 在 True 分支向检查器承诺更窄类型。
- `ParamSpec` 保留装饰器参数签名，`wraps` 保留运行时元数据。

```python
def first(items: list[T]) -> T: ...
```

## 易错点

检查 `Cache.get()` 应写 `is not None`，否则 `0`、`False` 等合法缓存值会被误判。类型兼容
关注完整函数签名；参数需要 `str` 的方法不能用接收 `User` 的实现替代。

## 快速自测

1. `list[int]` 为什么不能赋给 `list[object]`？
2. Protocol 与 BaseModel 的运行时职责有何不同？
3. ParamSpec 和 wraps 各保留什么？
