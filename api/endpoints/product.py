import json
from decimal import Decimal

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.dto import EmployeeDTO, UserDTO, ProductDTO, IngredientDTO, ProductWithIngredientsDTO
from api.models import Role, Table, Ingredient
from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.product_service import ProductService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент', 'Официант')
@provide_services
def get_menu(request, product_service: ProductService, **kwargs):
    return HttpResponse(
        jsonify(
            [
                ProductDTO.from_model(p)
                for p in product_service.get_all_products()
            ]
        )
    )


@get
@jwt_secured
@for_roles('Админ')
@provide_services
def get_analyze(request, order_service: OrderService, **kwargs):
    from_date_data = request.GET.get('fromdate', None)
    to_date_data = request.GET.get('todate', None)

    from_date = timify(from_date_data)
    to_date = timify(to_date_data)

    return HttpResponse(
        jsonify(
            [
                {
                    'product': ProductDTO.from_model(product),
                    'count': count
                }
                for product, count in order_service.analyze_sales(from_date, to_date)
            ]
        )
    )


@get
@jwt_secured
@for_roles('Админ')
@provide_services
def get_all_ingredients(request, product_service: ProductService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                IngredientDTO.from_model(i)
                for i in product_service.get_all_ingredients()
            ]
        )
    )


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def replenish_ingredients(request, product_service: ProductService = None, **kwargs):
    data = json.loads(request.body)

    names = [d['name']for d in data]
    counts = [d['count'] for d in data]

    product_service.replenish_ingredients(names, counts)

    return HttpResponse()


@get
@jwt_secured
@for_roles('Админ')
@provide_services
def get_products(request, product_service: ProductService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                ProductWithIngredientsDTO.from_model(product)
                for product in product_service.get_all_products()
            ]
        )
    )


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def add_product(request, product_service: ProductService = None, **kwargs):
    data = json.loads(request.body)

    price_data = data.get('price', None)
    name_data = data.get('name', None)
    ingredients_data = data.get('ingredients', None)

    if not price_data or not name_data or not ingredients_data:
        raise BadRequest('Все поля должны быть заполнены')

    price = Decimal(price_data)
    name = str(name_data)
    ingredients = list(Ingredient.objects.filter(id__in=[i['id'] for i in ingredients_data]))
    counts = [i['count'] for i in ingredients_data]

    product_service.add_product(name, price, ingredients, counts)

    return HttpResponse()


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def edit_product(request, product_id: int, product_service: ProductService = None, **kwargs):
    data = json.loads(request.body)

    price_data = data.get('price', None)
    name_data = data.get('name', None)
    ingredients_data = data.get('ingredients', None)

    if not price_data or not name_data or not ingredients_data:
        raise BadRequest('Все поля должны быть заполнены')

    price = Decimal(price_data)
    name = str(name_data)
    ingredients = list(Ingredient.objects.filter(id__in=[i['id'] for i in ingredients_data]))
    counts = [i['count'] for i in ingredients_data]

    product_service.edit_product(product_id, name, price, ingredients, counts)

    return HttpResponse()


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def delete_product(request, product_id: int, product_service: ProductService = None, **kwargs):
    product_service.delete_product(product_id)

    return HttpResponse()
