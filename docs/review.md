# Python 学习结业复习提纲

## 当前进度

目前已经完成本仓库的全部课程：Python 基础、面向对象、异常、
迭代与异步、常用标准库、Pydantic 2 和 pytest 实践。完整测试集为
24 项，当前全部通过。

| 模块 | 核心内容 |
|---|---|
| `basics.py` | 控制流、推导式、解包、模式匹配、真值 |
| `collections_demo.py` | list、tuple、dict、set |
| `functions.py` | 参数、闭包、高阶函数、装饰器 |
| `oop.py` | 类、property、dataclass、组合、Protocol、classmethod |
| `errors.py` | 异常转换、异常链、上下文管理器 |
| `iterators.py` | iterable、iterator、generator、惰性计算 |
| `async_demo.py` | coroutine、await、TaskGroup、async generator |
| `stdlib_demo.py` | Counter、defaultdict、JSON、islice、lru_cache |
| `pydantic_lab/` | 模型、约束、校验器、序列化、Settings |
| `tests/` | pytest、异常断言、参数化、临时环境变量 |

## 1. 基础语法

文件：`src/python_learning_lab/basics.py`

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

## 2. Python 容器

文件：`src/python_learning_lab/collections_demo.py`

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

## 3. 函数

文件：`src/python_learning_lab/functions.py`

### 参数类型

```python
def format_user(user_id, /, name, *, active=True):
    ...
```

- `/` 前面只能使用位置参数。
- `*` 后面只能使用关键字参数。

### 可变参数

```python
def total(*numbers):
    ...
```

`numbers` 是元组。

```python
def build_profile(name, **attributes):
    ...
```

`attributes` 是字典。

### 闭包

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply
```

内部函数离开外部函数后，仍然记得 `factor`。

### 装饰器

```python
@timed
def work():
    ...
```

近似于：

```python
work = timed(work)
```

装饰器在执行函数定义时应用，不是在调用被装饰函数时才创建。

## 4. 面向对象

文件：`src/python_learning_lab/oop.py`

### 类与对象

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius
```

- 类是模板。
- 对象是类的实例。
- `self` 是当前对象。
- `__init__` 初始化实例状态。

### Property

```python
@property
def radius(self):
    return self._radius

@radius.setter
def radius(self, value):
    ...
```

`@property` 创建名为 `radius` 的 property 对象，`@radius.setter` 给它添加赋值逻辑。

property 装饰器在执行类体时应用，属于运行时行为。

### Dataclass

```python
@dataclass(slots=True)
class Rectangle:
    width: float
    height: float
```

dataclass 自动生成初始化、表示和比较等方法。

初始化后的校验可以放在：

```python
def __post_init__(self):
    ...
```

### 组合

```python
@dataclass
class Drawing:
    shapes: list[Shape] = field(default_factory=list)
```

`Drawing` 拥有多个 `Shape`，这是 has-a 关系，不是继承。

可变的默认字段应使用：

```python
field(default_factory=list)
```

这样可以保证每个实例拥有独立列表。

### Protocol

```python
class Shape(Protocol):
    @property
    def area(self) -> float: ...
```

只要对象具有符合要求的 `area`，就能作为 `Shape` 使用，不要求显式继承。

### Classmethod

```python
@classmethod
def from_text(cls, text):
    ...
    return cls(...)
```

- `self` 代表实例。
- `cls` 代表类。
- classmethod 常用于具名构造方法。

已经完成的练习：

- `Temperature`
- `Product`
- `ShoppingCart`
- `BankAccount`

## 5. 异常处理

文件：`src/python_learning_lab/errors.py`

### 自定义异常

```python
class ConfigurationError(ValueError):
    pass
```

### 异常转换和异常链

```python
try:
    port = int(value)
except ValueError as error:
    raise ConfigurationError("端口必须是整数") from error
```

原则：只捕获真正知道怎样处理的异常。

```python
except FileNotFoundError:
    return None
```

不要无差别使用：

```python
except Exception:
    ...
```

### 上下文管理器

```python
@contextmanager
def temporary_value(...):
    try:
        yield
    finally:
        ...
```

- `yield` 前：进入 `with` 时执行。
- `yield` 后：离开 `with` 时执行。
- `finally`：无论正常结束还是出现异常，都会执行清理。

## 6. 迭代器和生成器

文件：`src/python_learning_lab/iterators.py`

最关键的关系：

```text
Iterable.__iter__() → Iterator

Iterator.__iter__() → 自己
Iterator.__next__() → 下一个值
```

所有 `Iterator` 都是 `Iterable`，但不是所有 `Iterable` 都是 `Iterator`。

```python
numbers = [1, 2, 3]       # Iterable
iterator = iter(numbers)  # Iterator
next(iterator)
```

### 手写迭代器

```python
def __next__(self):
    if self.current <= 0:
        raise StopIteration
```

### 生成器

```python
def fibonacci(limit):
    yield value
```

`yield` 返回一项、暂停函数并保存局部状态，下一次调用时继续。

### 委托迭代

```python
yield from group
```

近似于：

```python
for value in group:
    yield value
```

消费迭代器时不仅要关注返回值，还要避免意外多消费一项。

## 7. 异步编程

文件：`src/python_learning_lab/async_demo.py`

```python
async def fetch_user(...):
    await asyncio.sleep(...)
    return user
```

调用协程函数只会创建协程对象：

```python
coroutine = fetch_user(1)
```

使用 `await` 才会等待并取得结果：

```python
user = await fetch_user(1)
```

`await` 会暂停当前协程，把执行权交还给事件循环。

### 并发任务

```python
async with asyncio.TaskGroup() as group:
    task = group.create_task(fetch_user(1))
```

- coroutine 是异步工作说明。
- Task 是已交给事件循环调度的工作。
- 并发不等于多核并行。

### 异步生成器

```python
async def ticker():
    await ...
    yield value
```

通过 `async for` 消费：

```python
async for value in ticker():
    ...
```

`async for` 概念上相当于：

```python
iterator = aiter(values)

while True:
    try:
        value = await anext(iterator)
    except StopAsyncIteration:
        break
```

最外层入口：

```python
asyncio.run(main())
```

## 8. 常用标准库

文件：`src/python_learning_lab/stdlib_demo.py`

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

## 9. Pydantic 2

文件：`src/python_learning_lab/pydantic_lab/`

### BaseModel 和模型字段

```python
class User(BaseModel):
    name: str
    age: int = 18
```

`User` 确实继承 `BaseModel`。Pydantic 的元类会在创建 `User` 时读取
类型标注，把 `name` 和 `age` 从普通类属性转换为模型字段：

```python
User.model_fields["age"].default  # 18
```

创建实例后，经过校验的值进入实例：

```python
user = User(name="Ada", age="20")
user.__dict__  # {"name": "Ada", "age": 20}
```

真正的共享类属性需要显式使用 `ClassVar`：

```python
company: ClassVar[str] = "Python Lab"
```

### 字段约束和模型配置

```python
name: str = Field(min_length=2, max_length=50)
age: int = Field(ge=0, le=150)
```

常用约束包括 `gt`、`ge`、`lt`、`le`、`min_length`、
`max_length` 和 `pattern`。

```python
model_config = ConfigDict(
    extra="forbid",
    str_strip_whitespace=True,
)
```

- `extra="forbid"` 拒绝未声明字段。
- `str_strip_whitespace=True` 去除字符串两端空白。

### 字段和模型校验器

```python
@field_validator("tags", mode="before")
@classmethod
def normalize_tags(cls, value):
    ...
```

- `mode="before"` 接收原始输入，适合清洗和格式转换。
- 默认的 after 校验器接收已经完成标准类型校验的值。

```python
@model_validator(mode="after")
def admin_must_be_adult(self) -> Self:
    if self.role is Role.ADMIN and self.age < 18:
        raise ValueError("管理员必须年满 18 岁")
    return self
```

单字段规则使用 `field_validator`，跨字段规则使用 `model_validator`。

### 嵌套模型和数据边界

```text
UserCreate
→ 接收并校验外部注册输入

User
→ 系统内部完整对象，增加 UUID 和创建时间

UserPublic
→ 只包含允许公开的字段
```

Pydantic 可以把嵌套字典转换成真正的模型对象，错误路径也会保留为
`address.zip_code` 这样的完整位置。

### 默认工厂和计算字段

```python
id: UUID = Field(default_factory=uuid4)
created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC)
)
```

`default_factory` 在每次创建实例时调用，避免共享同一个动态默认值。

```python
@computed_field
@property
def display_name(self) -> str:
    return f"{self.name} ({self.role.value})"
```

`computed_field` 会让计算属性参与模型序列化。

### 序列化和 ValidationError

```python
model.model_dump()               # Python 字典
model.model_dump(mode="json")   # JSON 兼容字典
model.model_dump_json(indent=2)  # JSON 字符串
```

```python
for item in error.errors():
    item["loc"]
    item["type"]
    item["msg"]
```

程序判断错误类型时优先使用结构化的 `type`，不要依赖可能变化的完整
英文错误消息。

### Pydantic Settings

```python
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LAB_",
        env_file=".env",
    )

    debug: bool = False
    port: int = Field(default=8000, ge=1, le=65535)
```

环境变量本质上是字符串，Settings 负责读取、转换和校验：

```text
LAB_DEBUG=true → True
LAB_PORT=9000  → 9000
```

## 10. pytest 实践

文件：`tests/`

### 普通断言和异常断言

```python
assert user.age == 36

with pytest.raises(ValidationError) as captured:
    UserCreate.model_validate(payload)
```

### 参数化测试

```python
@pytest.mark.parametrize("quantity", [0, 100])
def test_invalid_quantity(quantity: int) -> None:
    ...
```

一份测试逻辑可以覆盖多个边界输入。

### 浮点数和临时环境

```python
assert cart.total == pytest.approx(898.0)
monkeypatch.setenv("LAB_PORT", "9000")
```

- `pytest.approx` 处理浮点数误差。
- `monkeypatch` 在测试后自动恢复临时环境。

测试不仅验证正确结果，还要覆盖非法输入、边界值、异常后的状态，以及
不应出现在公开输出中的敏感字段。

## 当前项目状态

- `take()` 已改为精确消费迭代器，不会额外取走一项。
- OOP 和 Pydantic 练习均已完成。
- Pydantic 练习的边界测试已经加入项目。
- 完整测试集为 24 项，全部通过。

## 复习自测

1. `Iterable` 和 `Iterator` 有什么区别？
2. `yield`、`return`、`await` 分别做什么？
3. 为什么迭代器通常只能消费一次？
4. `@property` 和 `@celsius.setter` 是什么时候应用的？
5. `self` 与 `cls` 有什么区别？
6. 为什么列表字段使用 `default_factory=list`？
7. 组合与继承有什么区别？
8. 为什么只捕获能够处理的异常？
9. `async for` 的每一轮如何取得下一项？
10. `TaskGroup` 与依次 `await` 有什么区别？
11. `Counter` 和 `defaultdict` 分别适合什么问题？
12. `lru_cache` 为什么能显著加快递归斐波那契？
13. `BaseModel` 怎样把类体中的字段声明转换成模型字段？
14. `ClassVar` 和 Pydantic 模型字段有什么区别？
15. before 和 after 字段校验器分别适合什么情况？
16. 为什么输入模型、内部模型和公开模型要分开？
17. `model_dump(mode="json")` 与 `model_dump_json()` 有什么区别？
18. `pytest.raises`、`parametrize` 和 `monkeypatch` 分别解决什么问题？

## 后续复习方式

1. 一周后不看源码回答上面的 18 个问题。
2. 只看测试，重新实现一个练习模型或函数。
3. 为购物车补充“购买数量不能超过库存”的跨字段校验。
4. 做一个小型综合项目，把 JSON、Pydantic、异常、生成器和 pytest 串起来。
