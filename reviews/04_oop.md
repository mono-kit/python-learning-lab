<!-- review-chapter: 4 -->

# 第 4 章快速复习：面向对象

## 一分钟速记

- 类定义对象的行为，实例保存各自状态；普通方法通过描述器绑定 `self`。
- `@property` 创建描述器；`@name.setter` 调用的是前面创建的 property 对象。
- 装饰器和类体都在运行时执行，不需要额外导入属性名。
- dataclass 可生成初始化、表示和比较，`__post_init__` 处理构造后校验。
- 可变字段使用 `field(default_factory=list)`，避免多个实例共享一个 list。
- 组合表达 has-a，继承表达 is-a；优先根据真实关系选择。
- Protocol 按能力匹配，不要求实现类显式继承。

```python
@property
def celsius(self) -> float:
    return self._celsius
```

## 易错点

实例属性通常存进 `instance.__dict__`，类属性存进 `Class.__dict__`。数据描述器会优先于
实例字典。`BaseModel` 会在创建类时读取字段声明并生成自己的字段机制，因此不能把它
简单理解为普通类属性赋值。

## 快速自测

1. `@celsius.setter` 中的 `celsius` 从哪里来？
2. 为什么 `default_factory=list` 能避免共享默认值？
3. 什么时候应使用组合而不是继承？
