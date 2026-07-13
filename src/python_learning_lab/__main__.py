from .basics import describe_number
from .collections_demo import unique_words
from .functions import make_multiplier
from .oop import Circle


def main() -> None:
    """运行一组最小演示，确认项目已经正确安装。"""
    print("Python Learning Lab")
    print(describe_number(7))
    print(unique_words("python makes learning python fun"))
    print(make_multiplier(3)(4))
    print(f"圆面积：{Circle(2).area:.2f}")


if __name__ == "__main__":
    main()

