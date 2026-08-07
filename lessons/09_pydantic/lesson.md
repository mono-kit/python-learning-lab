<!-- course-chapter: 9 -->

# 第 9 章：Pydantic 2

Pydantic 读作“派丹提克”。它利用 Python 类型标注验证外部数据，并把字典、JSON、环境变量等输入转换成程序内部对象。

## 1. 第一个模型

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

user = User(name="Ada", age="18")
assert user.age == 18
```

类型标注既服务于编辑器和类型检查器，也被 Pydantic 在运行时读取。默认模式允许合理转换，例如字符串 `"18"` 转为整数 `18`；在 `Field(strict=True)` 中可以禁止这种转换。

## 2. 字段约束

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0)
```

常用约束包括 `gt`、`ge`、`lt`、`le`、`min_length`、`max_length` 和 `pattern`。

## 3. 校验器

- `@field_validator`：处理单个字段
- `@model_validator`：检查多个字段之间的关系
- `mode="before"`：在标准类型转换前运行
- 默认的 `mode="after"`：在模型构造完成后运行

本项目在 `models.py` 中先标准化名字和标签，再验证管理员必须成年。

## 4. 嵌套模型

`UserCreate` 的 `address` 字段是 `Address`。即使输入是嵌套字典，最终也会得到真正的 `Address` 对象：

```python
user.address.city
```

校验错误的位置会包含完整路径，例如 `address.zip_code`。

## 5. 序列化

```python
user.model_dump()              # Python 字典
user.model_dump(mode="json")  # 只含 JSON 兼容值
user.model_dump_json(indent=2) # JSON 字符串
```

`model_validate()` 从 Python 对象构造模型，`model_validate_json()` 直接读取 JSON。

## 6. ValidationError

不要只显示一个模糊的“输入错误”。`error.errors()` 会给出结构化的错误列表，可用于 API 返回值、表单提示或日志。

## 7. Settings

`pydantic-settings` 把环境变量映射为类型安全配置。本项目使用 `LAB_` 前缀，例如：

```bash
export LAB_DEBUG=true
export LAB_PORT=9000
```

然后 `AppSettings()` 会完成布尔值和整数转换及范围校验。

## 推荐阅读顺序

1. `example/package/models.py`
2. `example/package/service.py`
3. `example/package/settings.py`
4. `example/package/main.py`
5. `exercise.py`
6. `test_lesson.py`
