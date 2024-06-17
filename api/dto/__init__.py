from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from api.models import User, Promo, Order, OrderProduct, Product, Role, Ingredient, Table, ProductIngredient


@dataclass
class RoleDTO:
    id: int
    name: str
    
    @staticmethod
    def from_model(role: Role) -> 'RoleDTO':
        return RoleDTO(role.id, role.name)


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
class IngredientDTO:
    id: int
    name: str
    count: int

    @staticmethod
    def from_model(ingredient: Ingredient) -> 'IngredientDTO':
        return IngredientDTO(ingredient.id, ingredient.name, ingredient.count)


@dataclass
class ProductDTO:
    id: int
    name: str
    price: Decimal

    @staticmethod
    def from_model(product: Product) -> 'ProductDTO':
        return ProductDTO(product.id, product.name, product.price)


@dataclass
class ProductWithIngredientsDTO:
    id: int
    name: str
    price: Decimal
    ingredients: list[IngredientDTO]

    @staticmethod
    def from_model(product: Product) -> 'ProductWithIngredientsDTO':
        return ProductWithIngredientsDTO(
            product.id,
            product.name,
            product.price,
            [
                IngredientDTO(
                    ingredient.ingredient_id,
                    ingredient.ingredient.name,
                    ingredient.count
                )
                for ingredient in ProductIngredient.objects.filter(product_id=product.id).all()
            ]
        )


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
    address: str | None
    table: int | None
    status: str
    products: list[OrderProductDTO]

    @staticmethod
    def from_model(order: Order) -> 'OrderDTO':
        return OrderDTO(
            order.id,
            order.date,
            order.address,
            order.table.id if order.table else None,
            order.status,
            [
                OrderProductDTO(
                    order_product.product.id,
                    order_product.product.name,
                    order_product.product.price,
                    order_product.count
                ) for order_product in OrderProduct.objects.filter(order_id=order.id).all()
            ]
        )


@dataclass
class TableDTO:
    id: int
    waiter_id: int | None
    client_id: int | None

    @staticmethod
    def from_model(table: Table) -> 'TableDTO':
        return TableDTO(
            table.id,
            table.client_id if table.client else None,
            table.waiter_id if table.waiter else None
        )
