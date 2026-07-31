from pathlib import Path
import runpy

import pytest
from pydantic import ValidationError


exercise = runpy.run_path(
    Path(__file__).parents[1] / "exercises" / "04_pydantic.py"
)
Product = exercise["Product"]
CartItem = exercise["CartItem"]
Cart = exercise["Cart"]


def test_product_converts_and_validates_fields() -> None:
    product = Product(name="机械键盘", price="399.5", stock=10)

    assert product.name == "机械键盘"
    assert product.price == 399.5
    assert isinstance(product.price, float)
    assert product.stock == 10


@pytest.mark.parametrize(
    ("values", "error_type"),
    [
        ({"name": "", "price": 100, "stock": 1}, "string_too_short"),
        ({"name": "键盘", "price": 0, "stock": 1}, "greater_than"),
        ({"name": "键盘", "price": -1, "stock": 1}, "greater_than"),
        ({"name": "键盘", "price": 100, "stock": -1}, "greater_than_equal"),
    ],
)
def test_product_rejects_invalid_fields(
    values: dict[str, object], error_type: str
) -> None:
    with pytest.raises(ValidationError) as captured:
        Product.model_validate(values)

    assert captured.value.errors()[0]["type"] == error_type


def test_cart_item_converts_nested_product() -> None:
    item = CartItem.model_validate(
        {
            "product": {"name": "机械键盘", "price": 399.5, "stock": 10},
            "quantity": 2,
        }
    )

    assert isinstance(item.product, Product)
    assert item.quantity == 2


@pytest.mark.parametrize("quantity", [0, 100])
def test_cart_item_rejects_quantity_outside_range(quantity: int) -> None:
    with pytest.raises(ValidationError):
        CartItem(
            product=Product(name="机械键盘", price=399.5, stock=10),
            quantity=quantity,
        )


def test_cart_computes_total_and_serializes_computed_field() -> None:
    cart = Cart.model_validate(
        {
            "items": [
                {
                    "product": {"name": "机械键盘", "price": 399.5, "stock": 10},
                    "quantity": 2,
                },
                {
                    "product": {"name": "鼠标", "price": 99.0, "stock": 20},
                    "quantity": 1,
                },
            ]
        }
    )

    assert cart.total == pytest.approx(898.0)
    assert cart.model_dump()["total"] == pytest.approx(898.0)


def test_cart_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError) as captured:
        Cart.model_validate({"items": [], "coupon": "SAVE10"})

    assert captured.value.errors()[0]["type"] == "extra_forbidden"
