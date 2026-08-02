"""完成后，可在本文件旁边编写 pytest 测试验证边界情况。"""

from pydantic import BaseModel, Field, ConfigDict, computed_field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class CartItem(BaseModel):
    product: Product
    quantity: int = Field(ge=1, le=99)


class Cart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CartItem]

    @computed_field
    @property
    def total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

if __name__ == "__main__":
    product = Product(
        name="机械键盘",
        price="399.5",
        stock=10,
    )

    print(product.name)         # 机械键盘
    print(product.price)        # 399.5
    print(type(product.price))  # float
    print(product.stock)        # 10
    