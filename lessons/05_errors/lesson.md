<!-- course-chapter: 5 -->

# 第 5 章：异常与上下文管理器

文件：`exercise.py`

### 自定义异常

```python
class ConfigurationError(ValueError):
    pass
```

### 异常转换和异常链

```python
try:
    port = int(value)
except ValueError as error:
    raise ConfigurationError("端口必须是整数") from error
```

原则：只捕获真正知道怎样处理的异常。

```python
except FileNotFoundError:
    return None
```

不要无差别使用：

```python
except Exception:
    ...
```

### 上下文管理器

```python
@contextmanager
def temporary_value(...):
    try:
        yield
    finally:
        ...
```

- `yield` 前：进入 `with` 时执行。
- `yield` 后：离开 `with` 时执行。
- `finally`：无论正常结束还是出现异常，都会执行清理。

### 异常边界与 with 协议

`try` 的 `else` 只在没有异常时执行，适合把“可能失败的最小代码”与成功路径分开；
`finally` 无论是否异常都会执行，适合释放资源。`raise` 会重新抛出当前异常，
`raise NewError(...) from error` 则把低层原因保存在 `__cause__` 中。

```python
try:
    value = parse(text)
except ValueError as error:
    raise ConfigurationError("配置格式错误") from error
else:
    use(value)
finally:
    cleanup()
```

`with manager as value` 本质上先调用 `manager.__enter__()`，离开时调用
`manager.__exit__(exc_type, exc, traceback)`。`__exit__` 返回真值会抑制异常，因此除非
契约明确，清理代码不应意外返回 `True`。完成后运行：

```bash
uv run pytest lessons/05_errors/test_lesson.py -q
```
