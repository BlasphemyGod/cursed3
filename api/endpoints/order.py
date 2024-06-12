import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from api.dto import EmployeeDTO, UserDTO, BookingDTO
from api.models import Role, Table, User, Order, Product
from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент')
@provide_services
def get_booking(request, user: User, order_service: OrderService = None, **kwargs):
    booking = order_service.get_user_booking(user)

    if booking:
        return HttpResponse(jsonify(BookingDTO(booking.id, booking.table.id, booking.date)), content_type='application/json')

    return HttpResponse('null', content_type='application/json')


@post
@jwt_secured
@for_roles('Клиент')
@provide_services
def book_table(request, user: User = None, order_service: OrderService = None, **kwargs):
    data = json.loads(request.body)

    time = timify(data.get('date', None))
    table = data.get('table', None)

    if table is None:
        raise BadRequest('Необходимо указать стол')

    try:
        order_service.book_table(user, time, Table.objects.get(id=table))

        return HttpResponse()
    except ValueError as e:
        raise BadRequest(f'{e}')


@post
@jwt_secured
@for_roles('Клиент')
@provide_services
def cancel_booking(request, user: User = None, order_service: OrderService = None, **kwargs):
    booking = order_service.get_user_booking(user)

    if booking is None:
        raise BadRequest('Брони не существует')

    order_service.cancel_order(booking)


@get
@jwt_secured
@for_roles('Клиент')
@provide_services
def get_user_orders(request, user: User = None, order_service: OrderService = None, **kwargs):
    return HttpResponse(
        jsonify(
            list(
                filter(
                    lambda o: o.client.id == user.id,
                    order_service.get_orders(None, [])
                )
            )
        ),
        content_type='application/json'
    )


@post
@jwt_secured
@for_roles('Официант', 'Курьер')
@provide_services
def change_order_status(request, order_id: int, order_service: OrderService = None, **kwargs):
    order = get_object_or_404(Order, id=order_id)

    order_service.change_order_status(order, request.body)

    return HttpResponse()


@post
@jwt_secured
@for_roles('Официант', 'Клиент')
@provide_services
def create_order(request, user: User = None, order_service: OrderService = None, **kwargs):
    data = json.loads(request.body)

    address_data = data.get('address', None)
    table_data = data.get('table', None)
    products = data.get('products', None)

    if address_data and table_data or not address_data and not table_data:
        raise BadRequest('Заказ может быть только в зале или на доставку')

    table = None

    if table_data:
        table = Table.objects.get(id=table_data)

    products_list = Product.objects.filter(id__in=list(map(lambda x: x['id'], products)))
    counts_list = list(map(lambda x: x['count'], products))

    order_service.create_order(user, table, address_data, list(zip(products_list, counts_list)))

    return HttpResponse()
