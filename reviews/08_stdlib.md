<!-- review-chapter: 8 -->

# 第 8 章快速复习：常用标准库

## 一分钟速记

- `Counter` 统计元素频次，`most_common()` 取高频项。
- `defaultdict(factory)` 在缺键时调用 factory 创建默认值。
- `itertools.islice` 惰性截取 iterable，不会复制整个序列。
- `json.dumps/loads` 处理字符串，`dump/load` 处理文件对象。
- `pathlib.Path` 用对象表达路径，避免手工拼分隔符。
- `lru_cache` 用空间换重复计算，参数必须可哈希。

```python
counts = Counter(words)
groups = defaultdict(list)
```

## 易错点

缓存可能无限增长或返回过期值，先看 `cache_info()` 的命中率。JSON key 必须是字符串等
兼容类型，datetime 和自定义对象需要显式转换。

## 快速自测

1. `defaultdict(list)` 中传的是 `list` 还是 `list()`？
2. `islice` 返回 list 吗？
3. 什么时候缓存反而会浪费内存？
