"""第 9 章映射：lessons/09_pydantic/exercise.py。"""

import pytest
from pydantic import ValidationError

from lessons._loader import load_exercise

exercise = load_exercise("09_pydantic")
Product = exercise["Product"]
CartItem = exercise["CartItem"]
Cart = exercise["Cart"]


def test_pydantic_converts_nested_input_and_computes_total() -> None:
    cart = Cart.model_validate(
        {
            "items": [
                {
                    "product": {"name": "Keyboard", "price": "399.5", "stock": 10},
                    "quantity": 2,
                }
            ]
        }
    )

    assert isinstance(cart.items[0], CartItem)
    assert isinstance(cart.items[0].product, Product)
    assert cart.items[0].product.price == 399.5
    assert cart.total == pytest.approx(799.0)
    assert cart.model_dump()["total"] == pytest.approx(799.0)


def test_pydantic_rejects_constraints_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Product(name="", price=1, stock=0)
    with pytest.raises(ValidationError):
        Cart.model_validate({"items": [], "coupon": "SAVE10"})
