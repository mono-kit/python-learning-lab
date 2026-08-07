<!-- course-chapter: 8 -->

# 第 8 章：常用标准库

文件：`exercise.py`

标准库通常应是工程选型的第一站：它随 Python 一起发布、无需增加依赖，也能减少版本
兼容和供应链维护成本。只有标准库无法清晰表达需求时，再评估第三方库。

### Counter

```python
counts = Counter(words)
counts.most_common(3)
```

适合统计元素出现次数。

### defaultdict

```python
groups = defaultdict(list)
groups[key].append(value)
```

适合自动创建默认容器并分组。

### JSON 与文件

```python
text = json.dumps(data, ensure_ascii=False, indent=2)
data = json.loads(text)
```

```python
path.write_text(text, encoding="utf-8")
text = path.read_text(encoding="utf-8")
```

### 迭代器切片

```python
tuple(islice(iterator, size))
```

### 赋值表达式

```python
while batch := get_batch():
    ...
```

### 递归与缓存

```python
@lru_cache(maxsize=None)
def fibonacci_recursive(number):
    ...
```

适合缓存“相同输入始终产生相同输出”的纯函数。
