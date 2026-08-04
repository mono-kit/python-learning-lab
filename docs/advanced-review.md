# Python 高级阶段复习笔记

## 当前进度

- 第 10 章“数据模型”已完成，`Version` 练习测试通过。
- 第 11 章“属性协议、描述器与 MRO”已完成，描述器练习测试通过。
- 第 12 章“高级类型标注”已完成，泛型缓存与装饰器练习测试通过。

这份文档只记录已经学懂的内容。完整学习顺序见
[`advanced-course.md`](advanced-course.md)。

## 11.1 属性协议与描述器

### 普通实例属性

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

普通赋值会把数据写入实例字典：

```python
user = User("Ada")
user.__dict__
# {"name": "Ada"}
```

没有描述器介入时，读取 `user.name` 可以直接从实例 `__dict__` 找到值。

### 描述器是什么

描述器是定义了以下一个或多个特殊方法的对象：

```python
__get__()
__set__()
__delete__()
```

当前课程使用的数据描述器：

```python
class NonEmptyString:
    def __set_name__(self, owner, name):
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{self.public_name} 不能为空")
        setattr(instance, self.storage_name, normalized)
```

描述器放在类上：

```python
class Account:
    name = NonEmptyString()
```

此时保存关系是：

```text
Account.__dict__["name"] → NonEmptyString 描述器对象
account.__dict__["_name"] → 某个实例自己的真实数据
```

核心原则：

> 描述器保存在类上，负责控制属性访问；真实值保存在实例上，每个实例互不影响。

### 类创建时的 `__set_name__`

执行 `class Account: ...` 时，Python 先执行类体，创建 `NonEmptyString` 对象并把
它绑定到名称 `name`。类创建完成后，Python 自动调用：

```python
descriptor.__set_name__(Account, "name")
```

参数含义：

```text
self  → 描述器对象
owner → Account 类
name  → "name"
```

描述器因此得到：

```text
public_name  → "name"
storage_name → "_name"
```

这个过程发生在执行类定义的运行时，不是传统意义上的编译阶段。

### 给描述器属性赋值

执行：

```python
account.name = "  Ada  "
```

由于 `Account.name` 实现了 `__set__`，Python 不会直接写入
`account.__dict__["name"]`，而是近似执行：

```python
descriptor = Account.__dict__["name"]
descriptor.__set__(account, "  Ada  ")
```

在 `__set__` 内：

```text
self     → 描述器对象
instance → account 实例
value    → "  Ada  "
```

描述器清理输入后执行：

```python
setattr(account, "_name", "Ada")
```

因此实例字典是：

```python
account.__dict__
# {"_name": "Ada"}
```

### 通过实例读取属性

执行：

```python
account.name
```

Python 发现类上的 `name` 是数据描述器，于是近似调用：

```python
descriptor.__get__(account, Account)
```

在 `__get__` 内：

```text
self     → 描述器对象
instance → account 实例
owner    → Account 类
```

描述器最终读取：

```python
getattr(account, "_name")
```

完整过程：

```text
account.name
→ 找到 Account.__dict__["name"] 数据描述器
→ 调用 descriptor.__get__(account, Account)
→ 读取 account._name
→ 返回 "Ada"
```

### 通过类读取属性

执行：

```python
Account.name
```

没有具体实例，因此近似调用：

```python
descriptor.__get__(None, Account)
```

描述器通常在 `instance is None` 时返回自己：

```python
if instance is None:
    return self
```

所以：

```python
Account.name is Account.__dict__["name"]
# True
```

`Account.__dict__["name"]` 是直接读取类字典中的原始对象；`Account.name` 会触发
描述器协议，只是当前实现又把描述器自己返回了。

### 数据描述器的查找优先级

同时实现 `__get__` 和 `__set__`（或 `__delete__`）的对象是数据描述器。读取
`account.name` 时，可以把属性查找顺序简化为：

```text
1. Account 及其 MRO 中的数据描述器
2. account.__dict__ 中的实例属性
3. Account 及其 MRO 中的普通类属性或非数据描述器
4. 仍未找到时调用 __getattr__
```

因此即使手动写入：

```python
account.__dict__["name"] = "假的名字"
```

读取：

```python
account.name
```

仍然优先调用数据描述器，并从 `_name` 返回 `"Ada"`。所以不能说“实例字典没有
`name` 才查找描述器”；数据描述器本来就排在实例字典之前。

### 多个实例如何隔离数据

```python
ada = Account("Ada", 36)
bob = Account("Bob", 40)
```

两个实例共享同一个行为对象：

```python
Account.__dict__["name"]
```

但真实值分别保存在：

```python
ada.__dict__["_name"]  # "Ada"
bob.__dict__["_name"]  # "Bob"
```

描述器不应该用 `self.value = value` 保存实例数据，因为描述器对象由所有实例共享，
这样会使实例互相覆盖。应把值写入传给 `__set__` 的 `instance`。

### `property` 与描述器

`property` 本身就是数据描述器：

```python
class Circle:
    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
```

其保存关系与自定义描述器相同：

```text
Circle.__dict__["radius"] → property 描述器
circle.__dict__["_radius"] → 实例真实数据
```

可以把自定义描述器理解为：把单个 property 的属性管理逻辑抽取成一个能够被多个
类和字段复用的对象。

### 速记

看到实例读取：

```python
account.name
```

联想到：

```python
Account.__dict__["name"].__get__(account, Account)
```

看到实例赋值：

```python
account.name = value
```

联想到：

```python
Account.__dict__["name"].__set__(account, value)
```

### 复习问题

1. 为什么 `account.__dict__` 中保存 `_name`，而不是 `name`？
2. `Account.name` 与 `account.name` 调用 `__get__` 时，`instance` 分别是什么？
3. 为什么 `account.__dict__["name"]` 不能遮蔽数据描述器？
4. 为什么描述器不能把每个账户的名字保存在 `descriptor.value` 中？
5. `property` 和自定义数据描述器在保存位置与访问流程上有什么共同点？

## 11.2 数据描述器、非数据描述器与方法绑定

数据描述器实现 `__get__`，并且还实现 `__set__` 或 `__delete__`；非数据描述器
只有 `__get__`。它们在默认属性查找中的位置不同：

```text
1. 类及其 MRO 中的数据描述器
2. 实例 __dict__
3. 类及其 MRO 中的非数据描述器或普通属性
4. __getattr__ 兜底
```

所以实例同名属性不能遮蔽数据描述器，却可以遮蔽非数据描述器。

### 函数为什么会变成绑定方法

类体中的函数是非数据描述器：

```python
class Handler:
    def process(self, trace):
        trace.append("handler")
        return trace
```

原始函数保存在：

```python
Handler.__dict__["process"]
```

通过实例读取时，函数的描述器协议近似执行：

```python
function = Handler.__dict__["process"]
method = function.__get__(handler, Handler)
```

产生的绑定方法记住：

```python
method.__self__ is handler       # True
method.__func__ is Handler.process  # True
```

所以：

```python
handler.process([])
```

近似于：

```python
Handler.process(handler, [])
```

`self` 不是特殊关键字，也不是凭空产生的参数；绑定方法在调用时自动把保存的实例
作为第一个参数传给原始函数。

调用：

```python
function.__get__(handler, Handler)
```

只显式写两个参数，是因为 `function.__get__` 本身已经绑定了描述器 `function`：

```python
type(function).__get__(function, handler, Handler)
```

其中三个参数依次是描述器 `self`、被访问实例 `instance` 和访问所经过的类
`owner`。

## 11.3 `__getattribute__` 与 `__getattr__`

每次执行：

```python
obj.name
```

都会先进入：

```python
obj.__getattribute__("name")
```

默认的 `object.__getattribute__` 负责数据描述器、实例字典和类属性等标准查找。
重写时应继续委托：

```python
def __getattribute__(self, name):
    print(f"正在读取：{name}")
    return object.__getattribute__(self, name)
```

不能在里面直接读取 `self.name` 或 `self.__dict__`，因为这些读取本身又会调用
`__getattribute__`，最终导致 `RecursionError`。

`__getattr__` 只在 `__getattribute__` 最终抛出 `AttributeError` 后调用：

```text
obj.attribute
→ __getattribute__("attribute")
→ 正常查找成功：直接返回
→ 正常查找失败并抛出 AttributeError
→ __getattr__("attribute")
```

`__getattr__` 应对不支持的名称继续抛出 `AttributeError`，否则拼写错误可能被静默
隐藏。

## 11.4 MRO 与协作式 `super()`

MRO 是 `Method Resolution Order`，即方法解析顺序。它决定 Python 在继承体系中
查找方法和类属性的线性顺序。

```python
class Service(LoggingMixin, MetricsMixin, Handler):
    pass
```

对应：

```python
Service.__mro__
```

```text
Service
→ LoggingMixin
→ MetricsMixin
→ Handler
→ object
```

MRO 只是查找顺序，不会自动执行其中每个同名方法。第一次找到
`LoggingMixin.process` 后查找就结束；后续实现能够执行，是因为每一层主动调用：

```python
super().process(trace)
```

`LoggingMixin.process` 中的零参数 `super()` 近似于：

```python
super(LoggingMixin, self)
```

它不是调用某个固定父类，而是在当前实例类型的 MRO 中，从 `LoggingMixin` 后面
继续查找。当前实例是 `Service`，所以下一项是 `MetricsMixin`，不是类声明中
`LoggingMixin` 的直接父类 `Handler`。

完整调用链：

```text
LoggingMixin.process
→ super()
→ MetricsMixin.process
→ super()
→ Handler.process
```

结果：

```python
["logging", "metrics", "handler"]
```

Python 使用 C3 linearization 计算 MRO。当前阶段记住三个约束即可：

1. 子类位于父类之前。
2. 类声明中靠左的直接父类通常优先。
3. 保持每个父类自身已有的 MRO 顺序。

构造方法遵守同一原则。Python 不会自动调用所有父类的 `__init__`；只有每一层
协作地调用 `super().__init__()`，初始化才会沿 MRO 继续。

### 第 11 章速记

```text
数据描述器压过实例字典；非数据描述器可以被实例字典遮蔽。
函数通过 __get__ 绑定实例，所以调用方法时 self 会被自动传入。
__getattribute__ 每次读取都执行，__getattr__ 只在查找失败后兜底。
MRO 决定去哪里找，super() 让执行沿 MRO 继续。
```

### 第 11 章复习问题

1. 为什么函数属于非数据描述器？
2. `handler.process.__self__` 和 `__func__` 分别是什么？
3. 为什么在 `__getattribute__` 中读取 `self.__dict__` 可能无限递归？
4. MRO 会不会自动执行所有同名方法？
5. 为什么 `LoggingMixin` 中的 `super()` 可能调用 `MetricsMixin`，而不是
   `Handler`？

## 12.1 类型标注的边界

Python 的类型标注主要供 mypy 等静态类型检查器使用，通常不会自动产生运行时
校验：

```python
def double(value: int) -> int:
    return value * 2


double("hello")
```

Python 不会仅仅因为实参不是 `int` 就拒绝调用。是否能运行仍取决于函数内部实际
执行的操作；需要运行时解析和校验外部数据时，应使用显式校验代码或 Pydantic 等
工具。

### `Any` 与 `object`

两者都可以接收任意 Python 对象，但交给类型检查器的信息完全不同：

```python
from typing import Any


def accept_any(value: Any) -> Any:
    return value


def accept_object(value: object) -> object:
    return value
```

`Any` 会关闭这一局部的类型检查：

```python
result = accept_any("hello")
result.upper()       # mypy 放行
result.not_exist()   # mypy 也可能放行，运行时才失败
```

`object` 表示“它可以是任何对象，但目前不知道具体是哪一种”，所以只能执行对所有
对象都安全的操作：

```python
result = accept_object("hello")
result.upper()  # mypy 报错：object 不保证具有 upper
```

速记：

```text
Any    → 不知道类型，并让类型检查器暂时不要检查
object → 不知道具体类型，所以只允许确定安全的操作
```

## 12.2 `TypeVar` 与泛型

`TypeVar` 表示一个暂时未知、但在同一次类型推断中必须保持一致的类型：

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T:
    return items[0]
```

调用：

```python
a = first([1, 2, 3])
b = first(["Python", "Java"])
```

推断过程：

```text
list[T] 与 list[int] 匹配 → T = int → a 是 int
list[T] 与 list[str] 匹配 → T = str → b 是 str
```

`TypeVar` 的重点不是“允许任意类型”，而是保存输入、存储和输出之间的关系。如果
返回类型改成 `object`，运行时仍会返回原来的元素，但类型检查器只知道结果是
`object`，关系就丢失了。

固定长度元组需要标注每个位置：

```python
def duplicate(value: T) -> tuple[T, T]:
    return value, value


duplicate(10)        # tuple[int, int]
duplicate("Python")  # tuple[str, str]
```

常见元组标注：

```text
tuple[int]       → 恰好一个 int
tuple[int, int]  → 恰好两个 int
tuple[int, ...]  → 任意数量的 int
```

### 泛型缓存保存键值关系

```python
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class Cache(Generic[K, V]):
    def __init__(self) -> None:
        self._values: dict[K, V] = {}

    def put(self, key: K, value: V) -> None:
        self._values[key] = value

    def get(self, key: K) -> V | None:
        return self._values.get(key)
```

具体使用时：

```python
cache: Cache[str, int] = Cache()
cache.put("answer", 42)
value = cache.get("answer")
```

类型契约是：

```text
K = str：put 和 get 的键必须是 str
V = int：put 的值必须是 int
get 的结果：int | None
```

`bound=Hashable` 限制键类型必须可哈希，因为底层字典要求键可哈希。

`get()` 返回 `V | None`，因此读取结果必须先收窄：

```python
if value is not None:
    print(value + 1)
```

不能用 `if value` 判断键是否存在，因为 `0`、空字符串等合法缓存值本身也是假值，
会与 `None` 混淆。

### 为什么不用 `dict[Any, Any]`

```python
loose_cache: dict[Any, Any] = {}
loose_cache[100] = "hello"
```

它很容易通过检查，是因为 `Any` 让检查器放弃了键和值的限制，而不是因为代码更
安全。`Cache[str, int]` 明确表达了调用方与实现方共同遵守的规则；如果只需要普通
字典，`dict[str, int]` 同样比 `dict[Any, Any]` 更能表达契约。

## 12.3 `Protocol`：按能力定义边界

`Protocol` 使用结构化子类型：实现方不必显式继承协议，只要具有签名兼容的方法和
属性，就能满足协议。

```python
class MessageStore(Protocol):
    def save(self, message: str) -> None: ...


def backup(store: MessageStore, message: str) -> None:
    store.save(message)
```

下面的类没有继承 `MessageStore`，但仍满足协议：

```python
class DatabaseStore:
    def save(self, message: str) -> None:
        print(f"保存：{message}")

    def delete_all(self) -> None:
        print("删除全部")
```

额外方法不会破坏协议兼容性。不过 `backup()` 内部把参数看作
`MessageStore`，因此只能依赖协议中声明的 `save()`，不能偷偷调用
`delete_all()`。

泛型协议还能保存多组类型关系：

```python
ID_contra = TypeVar("ID_contra", bound=Hashable, contravariant=True)
Item = TypeVar("Item")


class Repository(Protocol[ID_contra, Item]):
    def get(self, item_id: ID_contra) -> Item | None: ...
    def save(self, item: Item) -> None: ...
```

`Repository[int, User]` 表示 ID 必须是 `int`，保存和读取的实体必须是 `User`。
方法名相同还不够，参数与返回值的签名也必须兼容。这里 ID 只作为输入被消费，
所以协议将它标为逆变；先记住这是为了让协议的替换关系符合方法参数的兼容规则，
后续需要设计公共泛型接口时再深入协变与逆变。

## 12.4 `TypedDict` 与 `TypeGuard`

`TypedDict` 描述普通字典中每个已知键对应的类型：

```python
class UserRow(TypedDict):
    id: int
    name: str
    email: str | None
```

类型检查器因此知道：

```python
user["id"]     # int
user["name"]   # str
user["email"]  # str | None
```

运行时它仍然是普通 `dict`，不会像 Pydantic 一样自动验证或转换数据。

```text
TypedDict：为字典结构提供静态检查
dataclass：定义保存数据的运行时类，不自动校验类型
Pydantic：定义模型，并在运行时解析和校验输入
```

`email: str | None` 表示键必须存在，但值可以为 `None`，不表示该键可以省略。

### 自定义类型收窄

```python
class UserWithEmail(TypedDict):
    id: int
    name: str
    email: str


def has_email(user: UserRow) -> TypeGuard[UserWithEmail]:
    return isinstance(user.get("email"), str)
```

在正向分支中：

```python
if has_email(user):
    user["email"].upper()  # email 已收窄为 str
```

`TypeGuard` 告诉类型检查器，函数返回 `True` 时可以把参数看作目标类型。普通
`-> bool` 只描述返回值，不会自动表达这种类型含义。

当前课程中的 `TypeGuard` 只保证正向分支收窄；在 `else` 分支中，仍应把
`user["email"]` 看作原来的 `str | None`。

## 12.5 `ParamSpec` 与类型安全的装饰器

普通的 `Callable[..., Any]` 会丢掉被装饰函数的参数与返回类型。`ParamSpec`
保存完整参数规格，`TypeVar` 保存返回类型：

```python
P = ParamSpec("P")
R = TypeVar("R")


def traced(
    callback: Callable[[str], None],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            callback(function.__name__)
            return function(*args, **kwargs)

        return wrapper

    return decorate
```

这里：

```text
P        → 位置参数、关键字参数和关键字专用参数的完整规格
P.args   → wrapper 接收的位置参数
P.kwargs → wrapper 接收的关键字参数
R        → 返回类型
```

装饰前后都是 `Callable[P, R]`，所以 mypy 仍能检查原函数的调用签名。

### 装饰器工厂的展开过程

```python
@traced(calls.append)
def greet(name: str, *, punctuation: str = "!") -> str:
    return f"Hello {name}{punctuation}"
```

等价于：

```python
def greet(name: str, *, punctuation: str = "!") -> str:
    return f"Hello {name}{punctuation}"


greet = traced(calls.append)(greet)
```

拆成两步：

```python
decorator = traced(calls.append)  # 得到 decorate
greet = decorator(greet)          # 得到 wrapper
```

最终名称 `greet` 指向 `wrapper`。调用过程是：

```text
wrapper(...)
→ callback("greet")
→ 原始 greet(...)
→ 返回原始结果
```

`ParamSpec` 与 `wraps` 职责不同：

```text
ParamSpec → 为静态类型检查器保留参数与返回类型
wraps     → 在运行时保留 __name__、__doc__、__wrapped__ 等元数据
```

有 `@wraps(function)` 时，`greet.__name__` 是 `"greet"`；删除它以后，最终
暴露的是包装函数，所以 `greet.__name__` 是 `"wrapper"`，不是
`"decorate"`。

### 第 12 章速记

```text
Any 放弃检查；object 保持谨慎；TypeVar 保存类型关系。
Generic 把关系扩展到类；Protocol 按能力定义静态边界。
TypedDict 描述字典结构；TypeGuard 为自定义判断补充收窄语义。
ParamSpec 保存装饰器参数签名；wraps 保存运行时函数元数据。
```

### 第 12 章复习问题

1. 为什么 `Any` 比 `object` 更容易让错误逃到运行时？
2. `first(items: list[T]) -> T` 如何保存输入元素与返回值的类型关系？
3. 为什么检查 `Cache.get()` 的结果时应写 `is not None`，而不是直接判断真值？
4. 一个类为什么不继承 `Protocol` 也能满足它？
5. `TypedDict` 与 Pydantic 在运行时行为上有什么不同？
6. `TypeGuard` 的 `True` 分支向类型检查器承诺了什么？
7. `ParamSpec` 和 `wraps` 各自保留什么？
8. 为什么 `dict[Any, Any]` 没有表达键和值之间的类型契约？
