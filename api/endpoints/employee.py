import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.dto import EmployeeDTO, UserDTO, RoleDTO
from api.models import Role, Table, User
from api.services.employee_service import EmployeeService
from api.services.user_service import UserService
from api.utils import *


@post
@jwt_secured
@provide_services
@for_roles('Админ')
def new_employee(request, user_service: UserService = None, **kwargs):
    data = json.loads(request.body)

    login_data = data.get('login', None)
    password_data = data.get('password', None)
    first_name_data = data.get('first_name', None)
    last_name_data = data.get('last_name', None)
    phone_number_data = data.get('phone_number', None)
    role_id_data = data.get('role_id', None)

    if not (login_data and password_data and first_name_data and last_name_data and phone_number_data and role_id_data):
        raise BadRequest('Необходимо заполнить все поля')

    if user_service.get_user_by_login(login_data) is not None:
        raise BadRequest('Пользователь с таким логином уже существует')

    if not user_service.check_phone_number(phone_number_data):
        raise BadRequest('Этот номер уже существует в системе')

    result = user_service.add_user(
        login=login_data,
        password=password_data,
        first_name=first_name_data,
        last_name=last_name_data,
        phone_number=phone_number_data,
        role=Role.objects.get(id=role_id_data)
    )

    if not result:
        raise BadRequest('Не удалось создать пользователя')

    return HttpResponse()


@get
@jwt_secured
@provide_services
@for_roles('Админ', 'Работник зала')
def get_employees(request, employee_service: EmployeeService = None, **kwargs):
    employees = employee_service.get_all_employees()
    employees = [e for e in employees if e.role is None or e.role.name != 'Клиент']

    result = []
    for employee in employees:
        result.append(
            EmployeeDTO(
                UserDTO.from_model(employee),
                [shift.date for shift in employee.shifts.all()],
                [table.id for table in Table.objects.filter(waiter_id=employee.id)]
            )
        )

    return HttpResponse(jsonify(result), content_type='application/json')


@get
@jwt_secured
@provide_services
@for_roles('Курьер', 'Официант', 'Админ', 'Работник зала', 'Работник кухни')
def get_employee_shifts(request, user: User, employee_service: EmployeeService = None, **kwargs):
    return HttpResponse(
        jsonify(
            EmployeeDTO(
                UserDTO.from_model(user),
                [shift.date for shift in user.shifts.all()],
                [table.id for table in Table.objects.filter(waiter_id=user.id)]
            )
        ),
        content_type='application/json'
    )


@get
@jwt_secured
@provide_services
@for_roles('Админ')
def get_employees_roles(request, employee_service: EmployeeService = None, **kwargs):
    return HttpResponse(jsonify([RoleDTO.from_model(r) for r in employee_service.get_employees_roles()]), content_type='application/json')


@post
@jwt_secured
@provide_services
@for_roles('Админ')
def appoint_employee_to_shift(request, employee_service: EmployeeService = None, **kwargs):
    data = json.loads(request.body)

    employee_id = data.get('employee_id', None)
    date = data.get('date', None)

    employee = User.objects.get(id=employee_id)
    date = timify(date)

    employee_service.appoint_employee_to_shift(employee, date)

    return HttpResponse()


@post
@jwt_secured
@provide_services
@for_roles('Админ')
def remove_employee_from_shift(request, employee_service: EmployeeService = None, **kwargs):
    data = json.loads(request.body)

    employee_id = data.get('employee_id', None)
    date = data.get('date', None)

    employee = User.objects.get(id=employee_id)
    date = timify(date)

    employee_service.remove_employee_from_shift(employee, date)

    return HttpResponse()


@post
@jwt_secured
@provide_services
@for_roles('Админ')
def fire_employee(request, employee_id: int, **kwargs):
    User.objects.get(id=employee_id).delete()

    return HttpResponse()


@post
@jwt_secured
@provide_services
@for_roles('Работник зала')
def appoint_waiter_to_table(request, employee_service: EmployeeService = None, **kwargs):
    data = json.loads(request.body)

    employee_id = data.get('waiter_id', None)
    table_id = data.get('table_id', None)

    employee = User.objects.get(id=employee_id)
    table = Table.objects.get(id=table_id)

    employee_service.appoint_waiter_to_table(employee, table)

    return HttpResponse()
