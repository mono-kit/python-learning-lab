<!-- review-chapter: 9 -->

# 第 9 章快速复习：Pydantic 2

## 一分钟速记

- `BaseModel` 是继承；其元类在创建类时读取类型标注并建立字段定义。
- `age: int = 18` 在普通类中可表现为类属性，在 BaseModel 中则成为模型字段默认值。
- 外部字符串等输入可以按规则转换，`strict=True` 可关闭相应转换。
- `Field` 声明长度、范围和 pattern 等约束。
- `field_validator` 验证单字段，`model_validator` 验证跨字段关系。
- `model_validate()` 解析输入，`model_dump()` 和 `model_dump_json()` 序列化。
- 配置读取、领域对象和 API 模型应按边界选择，不必全部继承 BaseModel。

```python
class User(BaseModel):
    name: str
    age: int = 18
```

## 易错点

类型标注本身通常不做运行时校验，是 BaseModel 的类创建与实例化流程赋予了它字段语义。
模型字段可能不再以普通值形式留在类 `__dict__`，但这不等于源码声明“没有生效”。

## 快速自测

1. BaseModel 如何知道 `age` 是字段？
2. `model_dump()` 与直接读 `__dict__` 有何边界差异？
3. Pydantic 模型为什么适合放在系统输入输出边界？
