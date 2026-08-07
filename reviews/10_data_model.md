<!-- review-chapter: 10 -->

# 第 10 章快速复习：Python 数据模型

## 一分钟速记

- 运算符和内置函数会委托给特殊方法，例如 `a + b` 调用 `__add__`。
- 左操作返回 `NotImplemented` 后，Python 才可能尝试右侧的 `__radd__`。
- `NotImplemented` 是协议返回值，不是 `NotImplementedError`。
- 相等对象必须具有相同 hash；参与哈希的状态不应在入集合后改变。
- `dataclass(frozen=True)` 适合不可变值对象。
- 容器协议可通过 `__len__`、`__getitem__`、`__iter__`、`__contains__` 等实现。

```python
result = left.__add__(right)
if result is NotImplemented:
    result = right.__radd__(left)
```

## 易错点

对象进入 set/dict 后若影响 hash 的字段改变，原桶位置不再匹配，查找会失败而不是返回
`None`。不同类型比较应返回 `NotImplemented`，业务上非法的同类型运算可以抛领域异常。

## 快速自测

1. 为什么 `1 + money` 可能调用 `Money.__radd__`？
2. `a == b` 为真时，hash 必须满足什么？
3. 可变值对象为什么通常不应作为 dict key？
