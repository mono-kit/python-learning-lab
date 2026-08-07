<!-- course-chapter: 1 -->

# 第 1 章：基础语法

文件：`example.py`

### 控制流

```python
if number < 0:
    return "负数"
elif number == 0:
    return "零"
```

### 列表推导式

```python
[number**2 for number in numbers if number % 2 == 0]
```

### 序列解包

```python
name, age = person
```

### 模式匹配

```python
match payload:
    case {"type": "text", "content": str(content)}:
        ...
    case [first, *rest]:
        ...
```

### 真值判断

```python
return name if name else "匿名用户"
```

`None`、`False`、`0`、`""`、`[]` 和 `{}` 都是假值。

### 名字、对象与循环

赋值语句把名字绑定到对象，并不会为变量声明一个永久类型：

```python
value = 1
value = "one"
```

循环直接从可迭代对象取值；不需要手工维护下标时优先写 `for item in items`，需要位置时
使用 `enumerate(items, start=1)`。`range(stop)` 不包含 `stop`，所以 `range(3)` 产生
`0、1、2`。

模式匹配按 `case` 从上到下尝试，较具体的结构应放在较宽泛分支之前。推导式适合一眼能
读懂的“遍历、筛选、变换”；包含多层副作用或复杂异常处理时改用普通循环。

本章应能预测每个分支的返回值，区分“值为假”和“值是 `None`”，并解释为什么修改赋值
后的名字不会自动修改原先绑定的不可变对象。完成练习后运行：

```bash
uv run pytest lessons/01_basics/test_lesson.py -q
```
