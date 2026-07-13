"""完成后，可在本文件旁边编写 pytest 测试验证边界情况。"""

from pydantic import BaseModel


class Product(BaseModel):
    # TODO: name 长度 1..80；price > 0；stock >= 0
    pass


class CartItem(BaseModel):
    # TODO: 嵌套 Product；quantity 范围 1..99
    pass


class Cart(BaseModel):
    # TODO: items 是 CartItem 列表；禁止额外字段
    # TODO: 添加 computed_field total，计算总价格
    pass

