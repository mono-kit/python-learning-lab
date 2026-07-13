from dataclasses import dataclass


@dataclass
class BankAccount:
    owner: str
    balance: float = 0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("存款金额必须大于零")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("取款金额必须大于零")
        if amount > self.balance:
            raise ValueError("余额不足")
        self.balance -= amount

