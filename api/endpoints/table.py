import datetime
import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент', 'Официант', 'Работник зала', 'Админ')
def get_available_tables_by_date(request, order_service: OrderService = None, **kwargs):
    time = request.GET.get('time', None)

    time = timify(time)

    return HttpResponse(jsonify([t.id for t in order_service.get_available_tables(time)]), content_type='application/json')
