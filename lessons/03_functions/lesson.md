<!-- course-chapter: 3 -->

# 第 3 章：函数

文件：`example.py`

### 参数类型

```python
def format_user(user_id, /, name, *, active=True):
    ...
```

- `/` 前面只能使用位置参数。
- `*` 后面只能使用关键字参数。

### 可变参数

```python
def total(*numbers):
    ...
```

`numbers` 是元组。

```python
def build_profile(name, **attributes):
    ...
```

`attributes` 是字典。

### 闭包

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply
```

内部函数离开外部函数后，仍然记得 `factor`。

### 装饰器

```python
@timed
def work():
    ...
```

近似于：

```python
work = timed(work)
```

装饰器在执行函数定义时应用，不是在调用被装饰函数时才创建。

### 调用、作用域与元数据

默认参数在执行 `def` 时求值一次，因此可变默认值会被多次调用共享。常见写法是先用
`None` 表示“没有提供”，再在函数体内创建新容器：

```python
def collect(value, items=None):
    if items is None:
        items = []
    items.append(value)
    return items
```

闭包捕获的是名字所在的作用域，不是把某一时刻的值永久复制进去。循环里创建闭包时若要
冻结当前值，可以使用默认参数 `lambda value=value: value`。装饰器返回包装函数后，应
用 `functools.wraps` 保留原函数的 `__name__`、文档和 `__wrapped__`。

本章应能判断每个实参绑定到哪个形参，区分函数对象与调用结果，并解释
`@trace` 为什么等价于定义结束时执行 `function = trace(function)`。运行：

```bash
uv run pytest lessons/03_functions/test_lesson.py -q
```
