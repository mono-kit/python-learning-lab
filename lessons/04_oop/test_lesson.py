"""第 4 章映射：lessons/04_oop/exercise.py。"""

import pytest

from lessons._loader import load_exercise

exercise = load_exercise("04_oop")
Temperature = exercise["Temperature"]
Product = exercise["Product"]
ShoppingCart = exercise["ShoppingCart"]
BankAccount = exercise["BankAccount"]


def test_temperature_property_validates_assignment() -> None:
    temperature = Temperature(20)
    temperature.celsius = -273.15
    assert temperature.celsius == -273.15

    with pytest.raises(ValueError):
        temperature.celsius = -273.16
    assert temperature.celsius == -273.15


def test_product_validates_fields_and_computes_value() -> None:
    product = Product("Keyboard", price=399.5, quantity=2)
    assert product.total_value == pytest.approx(799.0)

    for values in [
        {"name": " ", "price": 1, "quantity": 0},
        {"name": "Keyboard", "price": 0, "quantity": 0},
        {"name": "Keyboard", "price": 1, "quantity": -1},
    ]:
        with pytest.raises(ValueError):
            Product(**values)


def test_shopping_carts_have_independent_item_lists() -> None:
    first = ShoppingCart()
    second = ShoppingCart()
    first.add(Product("Keyboard", price=100, quantity=2))

    assert first.total_price == 200
    assert second.items == []


def test_bank_account_rejects_invalid_transitions_without_mutation() -> None:
    account = BankAccount("Ada", balance=100)
    account.deposit(25)
    account.withdraw(40)
    assert account.balance == 85

    for operation in [lambda: account.deposit(0), lambda: account.withdraw(1000)]:
        with pytest.raises(ValueError):
            operation()
    assert account.balance == 85
