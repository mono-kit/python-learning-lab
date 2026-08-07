<!-- review-chapter: 2 -->

# 第 2 章快速复习：Python 容器

## 一分钟速记

- list 有序、可变、允许重复；tuple 有序且不可变。
- dict 保存键值映射，set 保存唯一元素；键和集合元素必须可哈希。
- `mapping[key]` 缺失时抛 `KeyError`，`mapping.get(key, default)` 返回默认值。
- `{**defaults, **user}` 创建新字典，后面的同名键覆盖前面。
- `a = b` 不复制容器；两个名字可能指向同一个可变对象。

```python
groups.setdefault(score, []).append(name)
unique_in_order = list(dict.fromkeys(values))
```

## 易错点

浅复制只复制最外层容器，内部可变对象仍共享。set 去重依赖相等与哈希，不承担“保留原
顺序”的语义。返回 `even, odd` 实际返回一个二元 tuple。

## 快速自测

1. 为什么 list 不能作为 dict 的键？
2. `second = first` 后修改 `second`，为什么 `first` 也可能变化？
3. 如何按字典的值把多个键归组？
