<!-- review-chapter: 6 -->

# 第 6 章快速复习：迭代器与生成器

## 一分钟速记

- Iterable 的 `__iter__()` 返回 Iterator。
- Iterator 的 `__iter__()` 返回自己，`__next__()` 返回下一项或抛 `StopIteration`。
- 所有 Iterator 都是 Iterable，但 Iterable 不一定是 Iterator。
- 生成器函数调用时不执行函数体，第一次 `next()` 才开始运行。
- `yield` 产出一项并保存局部状态，`yield from` 委托给另一个 iterable。
- 迭代器通常只能消费一次，已经取出的元素不会重新出现。

```python
iterator = iter([10, 20, 30])
first = next(iterator)
rest = list(iterator)
```

## 易错点

生成器中的参数校验也会推迟到第一次消费。生成器如果在 `with` 中暂停，资源仍保持打开；
正常耗尽、异常或 `close()` 都应触发清理。

## 快速自测

1. list 为什么是 Iterable 却不是 Iterator？
2. 上例中 `first` 和 `rest` 分别是什么？
3. 为什么对同一个生成器第二次循环通常没有结果？
