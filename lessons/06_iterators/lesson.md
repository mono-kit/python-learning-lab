<!-- course-chapter: 6 -->

# 第 6 章：迭代器与生成器

文件：`exercise.py`

最关键的关系：

```text
Iterable.__iter__() → Iterator

Iterator.__iter__() → 自己
Iterator.__next__() → 下一个值
```

所有 `Iterator` 都是 `Iterable`，但不是所有 `Iterable` 都是 `Iterator`。

```python
numbers = [1, 2, 3]       # Iterable
iterator = iter(numbers)  # Iterator
next(iterator)
```

### 手写迭代器

```python
def __next__(self):
    if self.current <= 0:
        raise StopIteration
```

### 生成器

```python
def fibonacci(limit):
    yield value
```

`yield` 返回一项、暂停函数并保存局部状态，下一次调用时继续。

### 委托迭代

```python
yield from group
```

近似于：

```python
for value in group:
    yield value
```

消费迭代器时不仅要关注返回值，还要避免意外多消费一项。

### 惰性、耗尽与资源

`iter(iterable)` 创建或取得迭代器，`next(iterator)` 才请求一个值。迭代器抛出
`StopIteration` 后表示耗尽，通常不能重新开始；list 等可迭代对象每次 `iter(list)`
则可创建新的迭代器。

生成器调用时只创建对象，函数体在第一次 `next()` 才开始执行。它适合流式处理和降低
峰值内存，但也意味着参数校验、文件打开和异常可能被推迟到消费时。生成器如果持有文件
等资源，应确保正常耗尽、异常或显式 `close()` 都能进入 `finally` 清理。

```python
iterator = fibonacci(3)
first = next(iterator)
remaining = list(iterator)
```

这里 `list(iterator)` 只得到尚未消费的部分。完成本章练习后运行：

```bash
uv run pytest lessons/06_iterators/test_lesson.py -q
```
