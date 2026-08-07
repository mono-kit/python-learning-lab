<!-- review-chapter: 3 -->

# 第 3 章快速复习：函数

## 一分钟速记

- `/` 前是仅位置参数，`*` 后是仅关键字参数。
- `*args` 收集为 tuple，`**kwargs` 收集为 dict。
- 默认参数在执行 `def` 时求值一次，可变默认值会被多次调用共享。
- 闭包保存外层名字所在的作用域，函数返回后仍可访问。
- `@decorator` 近似于定义完成时执行 `function = decorator(function)`。
- `functools.wraps` 保留原函数的名称、文档和 `__wrapped__`。

```python
def format_user(user_id, /, name, *, active=True): ...
```

## 易错点

循环中创建闭包时会发生晚绑定；需要冻结当前值可使用默认参数。不要写 `items=[]` 作为
可变默认值，改用 `None` 后在函数体内创建新 list。

## 快速自测

1. 调用装饰后的函数时，名字指向原函数还是包装函数？
2. `*args` 和调用时的 `*values` 分别做什么？
3. 闭包离开外层函数后为什么还能访问外层变量？
