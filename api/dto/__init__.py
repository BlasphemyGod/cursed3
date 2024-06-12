from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from api.models import User, Promo, Order, OrderProduct, Product


@dataclass
class UserDTO:
    id: int
    first_name: str
    last_name: str
    phone_number: str
    role_id: int
    role: str

    @staticmethod
    def from_model(user: User) -> 'UserDTO':
        return UserDTO(user.id, user.first_name, user.last_name, user.phone_number, user.role.id, user.role.name)


@dataclass
class EmployeeDTO:
    employee: UserDTO
    shifts: list[date]
    tables: list[int]


@dataclass
class PromoDTO:
    id: int
    text: str
    content: str

    @staticmethod
    def from_model(promo: Promo) -> 'PromoDTO':
        return PromoDTO(promo.id, promo.text, promo.content.url)


@dataclass
class BookingDTO:
    id: int
    table: int
    date: date


@dataclass
class ProductDTO:
    id: int
    name: str
    price: Decimal

    @staticmethod
    def from_model(product: Product) -> 'ProductDTO':
        return ProductDTO(product.id, product.name, product.price)


@dataclass
class OrderProductDTO:
    id: int
    name: str
    price: Decimal
    count: int


@dataclass
class OrderDTO:
    id: int
    date: datetime
    address: str
    table: int
    status: str
    products: list[OrderProductDTO]

    @staticmethod
    def from_model(order: Order) -> 'OrderDTO':
        return OrderDTO(
            order.id,
            order.date,
            order.address,
            order.table.id,
            order.status,
            [
                OrderProductDTO(
                    order_product.product.id,
                    order_product.product.name,
                    order_product.product.price,
                    order_product.product.count
                ) for order_product in OrderProduct.objects.filter(order_id=order.id).all()
            ]
        )