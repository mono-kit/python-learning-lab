<!-- course-chapter: 2 -->

# 第 2 章：Python 容器

文件：`example.py`

### 去重和排序

```python
sorted(set(words))
```

- `set` 去重。
- `sorted` 返回排序后的列表。

### 字典计数

```python
counts[word] = counts.get(word, 0) + 1
```

### 返回多个值

```python
return even, odd
```

Python 实际返回一个元组。

### 字典合并

```python
{**defaults, **user}
```

后面的值覆盖前面的同名键。该表达式创建新字典，不会修改原字典。

### 容器语义与选择

- `list` 有序、可变，允许重复，适合按位置访问和逐步追加；
- `tuple` 有序、不可变，适合表达固定结构；
- `dict` 保存键到值的映射，键必须可哈希；
- `set` 保存唯一、可哈希元素，适合去重和成员查询。

容器赋值默认不会复制对象：

```python
first = [1, 2]
second = first
second.append(3)
assert first == [1, 2, 3]
```

这里两个名字指向同一个 list。需要浅复制时可用 `first.copy()`；如果内部仍包含可变对象，
浅复制不会递归复制它们。字典的 `get()` 在键不存在时返回默认值，而 `mapping[key]` 会
抛出 `KeyError`，应根据“缺失是否正常”选择接口。

集合去重依赖相等与哈希契约，不保证保留输入顺序。需要“按首次出现顺序去重”时，可以
利用 dict 的插入顺序，例如 `list(dict.fromkeys(values))`。完成练习后运行：

```bash
uv run pytest lessons/02_collections/test_lesson.py -q
```
