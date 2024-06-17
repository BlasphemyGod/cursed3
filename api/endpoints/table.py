from datetime import date
import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.dto import TableDTO
from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент', 'Официант', 'Работник зала', 'Админ')
@provide_services
def get_available_tables_by_date(request, order_service: OrderService = None, **kwargs):
    time = request.GET.get('time', None)

    time = timify(time)

    return HttpResponse(jsonify([t.id for t in order_service.get_available_tables(time)]), content_type='application/json')


@get
@jwt_secured
@for_roles('Работник зала')
@provide_services
def get_tables(request, order_service: OrderService = None, **kwargs):
    tables = order_service.get_available_tables(date.today())
    tables_amount = len(tables)
    occupied_tables_amount = len(filter(lambda x: x.client is not None, tables))

    load = occupied_tables_amount / tables_amount

    return HttpResponse(
        jsonify(
            {
                'tables': [
                    TableDTO.from_model(t)
                    for t in tables
                ],
                'load': load
            }
        )
    )