<!-- course-chapter: 4 -->

# 第 4 章：面向对象

文件：`example.py`

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
