from collections.abc import Callable
from typing import TypeVar, ParamSpec
from functools import wraps

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")



def compose(first: Callable[[T], T], second: Callable[[T], T]) -> Callable[[T], T]:
    """返回一个新函数，新函数先调用 first，再调用 second。"""

    def wrapper(x: T) -> T:
        """先调用 first，再调用 second。"""
        result = first(x)
        result = second(result)
        return result

    return wrapper


def retry(attempts: int):
    """编写一个装饰器：函数抛出异常时最多重试 attempts 次。"""

    if attempts < 1:
        raise ValueError("attempts 必须大于等于 1")

    def outer_wrapper(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner_wrapper(*args, **kwargs) -> R:
            """最多重试 attempts 次。"""
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    if _ < attempts - 1:
                        continue
                    raise error

        return inner_wrapper

    return outer_wrapper


if __name__ == "__main__":

    def add_one(number: int) -> int:
        return number + 1

    def double(number: int) -> int:
        return number * 2

    combined = compose(add_one, double)
    reverse = compose(double, add_one)

    assert callable(combined)
    assert combined(3) == 8
    assert combined(0) == 2
    assert combined(-2) == -2
    assert reverse(3) == 7

    def remove_spaces(text: str) -> str:
        return text.strip()

    def make_uppercase(text: str) -> str:
        return text.upper()

    normalize = compose(remove_spaces, make_uppercase)

    assert normalize("  hello  ") == "HELLO"

    print("compose 全部验证通过")

    success_state = {"calls": 0}


    @retry(attempts=3)
    def always_success() -> int:
        success_state["calls"] += 1
        return 42


    assert always_success() == 42
    assert success_state["calls"] == 1
    assert always_success.__name__ == "always_success"

    unstable_state = {"calls": 0}
    @retry(attempts=3)
    def unstable(value: int, *, bonus: int = 0) -> int:
        unstable_state["calls"] += 1

        if unstable_state["calls"] < 3:
            raise RuntimeError("暂时失败")

        return value + bonus


    assert unstable(10, bonus=5) == 15
    assert unstable_state["calls"] == 3
    assert unstable.__name__ == "unstable"


    failure_state = {"calls": 0}
    @retry(attempts=3)
    def always_fail() -> None:
        failure_state["calls"] += 1
        raise RuntimeError("永远失败")


    try:
        always_fail()
    except RuntimeError as error:
        assert str(error) == "永远失败"
    else:
        raise AssertionError("always_fail 应该抛出 RuntimeError")

    assert failure_state["calls"] == 3

    single_state = {"calls": 0}


    @retry(attempts=1)
    def fail_once() -> None:
        single_state["calls"] += 1
        raise ValueError("失败")


    try:
        fail_once()
    except ValueError:
        pass
    else:
        raise AssertionError("fail_once 应该抛出 ValueError")

    assert single_state["calls"] == 1

    try:
        @retry(attempts=0)
        def invalid_retry() -> None:
            pass

    except ValueError as error:
        assert str(error) == "attempts 必须大于等于 1"
    else:
        raise AssertionError("retry(0) 应该抛出 ValueError")
    
    print("retry 全部验证通过")
