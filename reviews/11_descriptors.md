<!-- review-chapter: 11 -->

# 第 11 章快速复习：属性协议、描述器与 MRO

## 一分钟速记

- 数据描述器实现 `__set__`/`__delete__`，读取时优先于实例字典。
- 非数据描述器只实现 `__get__`，可以被实例同名属性遮蔽。
- 函数是非数据描述器；`function.__get__(instance, owner)` 创建绑定方法。
- `__getattribute__` 处理每次属性读取，失败后才调用 `__getattr__`。
- MRO 是 Method Resolution Order，决定多继承查找顺序。
- `super()` 表示从当前类在 MRO 的下一项继续，不是固定调用某个父类。

```text
数据描述器 → 实例 __dict__ → 非数据描述器/类属性 → __getattr__
```

## 易错点

`descriptor.__get__(handler, Handler)` 中 `self` 已由绑定调用自动传入，显式参数分别是
instance 和 owner。MRO 只决定查找，不会自动执行所有同名方法；协作式调用需要每一层
正确使用 `super()`。

## 快速自测

1. property 为什么通常是数据描述器？
2. 实例方法的 `__self__` 和 `__func__` 分别是什么？
3. 菱形继承中 `super()` 如何避免同一实现执行两次？
