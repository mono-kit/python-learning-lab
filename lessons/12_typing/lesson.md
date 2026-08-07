<!-- course-chapter: 12 -->

# 第 12 章：高级类型标注

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
