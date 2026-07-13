from pydantic import BaseModel, ConfigDict, Field, computed_field


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
