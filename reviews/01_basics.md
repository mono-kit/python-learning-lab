<!-- review-chapter: 1 -->

# 第 1 章快速复习：基础语法

## 一分钟速记

- 名字通过赋值绑定对象，Python 变量没有永久固定的运行时类型。
- `if/elif/else` 从上到下选择第一个满足的分支。
- `range(stop)` 不包含 `stop`；需要索引时用 `enumerate()`。
- 推导式适合简单的遍历、筛选和变换，复杂控制流改用普通循环。
- `None`、`False`、数字零、空字符串和空容器都为假，但含义不相同。
- `match/case` 从上到下匹配，具体模式放在宽泛模式之前。

```python
label = name if name else "匿名用户"
squares = [value**2 for value in values if value % 2 == 0]
```

## 易错点

判断“没有提供”通常写 `value is None`，不要用 `if not value` 把 `0`、`""` 等合法值
一起排除。FizzBuzz 要先判断 15 的倍数，否则会提前落入 3 或 5 的分支。

## 快速自测

1. `range(1, 4)` 产生哪些值？
2. `0 or 18` 的结果是什么？这与检查 `is None` 有何不同？
3. 列表推导式中筛选条件和结果表达式分别位于哪里？
