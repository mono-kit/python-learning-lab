<!-- review-chapter: 5 -->

# 第 5 章快速复习：异常与上下文管理器

## 一分钟速记

- 只捕获当前层真正知道如何处理或转换的异常。
- `raise NewError(...) from error` 保存异常原因链。
- `else` 只在 try 没有异常时执行，`finally` 无论如何都会执行。
- `with` 调用 `__enter__()`，退出时调用 `__exit__()`。
- `@contextmanager` 中 `yield` 前是进入逻辑，`yield` 后是退出逻辑。

```python
try:
    value = int(text)
except ValueError as error:
    raise ConfigurationError("配置错误") from error
```

## 易错点

不要用宽泛的 `except Exception` 静默吞错。`__exit__` 返回真值会抑制异常；清理资源时
若没有明确契约，不应意外返回 `True`。

## 快速自测

1. `finally` 在 return 或异常时是否执行？
2. `raise` 与 `raise ... from error` 有什么区别？
3. contextmanager 的代码为什么只写一个 `yield`？
