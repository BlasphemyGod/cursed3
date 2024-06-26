import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from api.dto import EmployeeDTO, UserDTO, BookingDTO, OrderDTO
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

    return HttpResponse()


@get
@jwt_secured
@for_roles('Клиент', 'Официант', 'Курьер')
@provide_services
def get_user_orders(request, user: User = None, order_service: OrderService = None, **kwargs):
    officiant_tables = [t.id for t in Table.objects.filter(waiter_id=user.id).all()]
    return HttpResponse(
        jsonify(
            list(
                map(
                    lambda order: OrderDTO.from_model(order),
                    filter(
                        lambda o: o.client.id == user.id or o.table_id in officiant_tables or o.courier_id == user.id,
                        order_service.get_orders(None, [] if user.role.name not in ('Официант',) else officiant_tables)
                    )
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

    order_service.change_order_status(order, request.body.decode('utf8'))

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


@get
@jwt_secured
@for_roles('Админ')
@provide_services
def get_delivery_orders(request, order_service: OrderService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                OrderDTO.from_model(o)
                for o in order_service.get_delivery_orders()
            ]
        )
    )


@get
@jwt_secured
@for_roles('Админ')
@provide_services
def get_unfinished_delivery_orders(request, order_service: OrderService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                OrderDTO.from_model(o)
                for o in order_service.get_unfinished_delivery_orders()
            ]
        )
    )


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def appoint_courier_to_order(request, employee_service: EmployeeService = None, **kwargs):
    data = json.loads(request.body)

    courier_id_data = data.get('courier_id', None)
    order_id_data = data.get('order_id', None)

    if not courier_id_data or not order_id_data:
        raise BadRequest('Хотя бы одно поле должно быть заполнено')

    employee = User.objects.get(id=courier_id_data)
    order = Order.objects.get(id=order_id_data)

    employee_service.appoint_courier_to_order(employee, order)

    return HttpResponse()


@get
@jwt_secured
@for_roles('Работник кухни')
@provide_services
def get_active_orders(request, order_service: OrderService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                OrderDTO.from_model(o)
                for o in order_service.get_orders(
                    'Принят',
                    []
                ) +
                order_service.get_orders(
                    'Готовится',
                    []
                )
            ]
        )
    )
