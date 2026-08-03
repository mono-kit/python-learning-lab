"""第 12 章：泛型、Protocol、类型收窄和保留签名的装饰器。"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator
from functools import wraps
from typing import Generic, ParamSpec, Protocol, TypedDict, TypeGuard, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")


class Cache(Generic[K, V]):
    """K 和 V 保存键、值之间的静态类型关系。"""

    def __init__(self) -> None:
        self._values: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._values.get(key)

    def put(self, key: K, value: V) -> None:
        self._values[key] = value

    def __contains__(self, key: object) -> bool:
        return key in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[K]:
        return iter(self._values)


ID_contra = TypeVar("ID_contra", bound=Hashable, contravariant=True)
Item = TypeVar("Item")


class Repository(Protocol[ID_contra, Item]):
    def get(self, item_id: ID_contra) -> Item | None: ...

    def save(self, item: Item) -> None: ...


class UserRow(TypedDict):
    id: int
    name: str
    email: str | None


class UserWithEmail(TypedDict):
    id: int
    name: str
    email: str


def has_email(user: UserRow) -> TypeGuard[UserWithEmail]:
    """TypeGuard 告诉类型检查器：True 分支中的 email 一定是 str。"""

    return isinstance(user.get("email"), str)


def traced(callback: Callable[[str], None]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """ParamSpec 保留被装饰函数的所有参数类型。"""

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            callback(function.__name__)
            return function(*args, **kwargs)

        return wrapper

    return decorate


def main() -> None:
    cache: Cache[str, int] = Cache()
    cache.put("answer", 42)
    print(cache.get("answer"))

    calls: list[str] = []

    @traced(calls.append)
    def add(left: int, right: int) -> int:
        return left + right

    print(add(2, 3), calls)


if __name__ == "__main__":
    main()
