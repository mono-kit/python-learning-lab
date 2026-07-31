from dataclasses import dataclass

class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        # 返回内部保存的数据
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        # 温度不能低于绝对零度 -273.15
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度 -273.15")
        self._celsius = value

@dataclass(slots=True)
class Product:
    name: str
    price: float
    quantity: int = 0

    def __post_init__(self) -> None:
        # name 不能为空
        # price 必须大于零
        # quantity 不能小于零
        if self.name.strip() == "":
            raise ValueError("产品名称不能为空")
        if self.price <= 0:
            raise ValueError("产品价格必须大于零")
        if self.quantity < 0:
            raise ValueError("产品数量不能小于零")

    @property
    def total_value(self) -> float:
        # price * quantity
        return self.price * self.quantity

from dataclasses import dataclass, field

@dataclass
class ShoppingCart:
    items: list[Product] = field(default_factory=list)

    def add(self, product: Product) -> None:
        # 添加商品
        self.items.append(product)

    @property
    def total_price(self) -> float:
        # 计算所有商品价格之和
        return sum(item.total_value for item in self.items)

@dataclass
class BankAccount:
    owner: str
    balance: float = 0

    def deposit(self, amount: float) -> None:
        """存入正数金额，否则抛出 ValueError。"""
        if amount <= 0:
            raise ValueError("存款金额必须大于零")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """取款；金额无效或余额不足时抛出 ValueError。"""
        if amount <= 0:
            raise ValueError("取款金额必须大于零")
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount

