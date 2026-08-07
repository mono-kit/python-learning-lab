<!-- review-chapter: 13 -->

# 第 13 章快速复习：流式处理与资源管理

## 一分钟速记

- 生成器惰性执行，第一次 `next()` 才进入函数体。
- 暂停在 `with` 内的 `yield` 时，资源保持打开。
- 正常耗尽、异常和 `close()` 都应让 `finally` 执行。
- 迭代器是单次消费的；不要为“检查”偷偷多取一项。
- 批次产出后使用新 list，避免后续修改已经交给调用方的对象。
- `raise DomainError(...) from error` 保存原始解析错误。
- `ExitStack` 管理动态数量资源，并按进入的相反顺序退出。

```python
with ExitStack() as stack:
    files = [stack.enter_context(open(path)) for path in paths]
```

## 易错点

生成器返回类型写成 Iterator 不能单独证明内部没有先加载全部数据。若要让参数立即校验，
可用普通外层函数检查后返回内部生成器。

## 快速自测

1. 为什么 `generator.close()` 会执行清理？
2. 为什么批次产出后不能调用原 list 的 `clear()`？
3. ExitStack 的退出顺序是什么？
