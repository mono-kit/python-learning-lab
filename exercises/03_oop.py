from dataclasses import dataclass


@dataclass
class BankAccount:
    owner: str
    balance: float = 0

    def deposit(self, amount: float) -> None:
        """存入正数金额，否则抛出 ValueError。"""
        raise NotImplementedError

    def withdraw(self, amount: float) -> None:
        """取款；金额无效或余额不足时抛出 ValueError。"""
        raise NotImplementedError

