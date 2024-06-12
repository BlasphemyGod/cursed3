import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.dto import UserDTO
from api.models import Role
from api.services.user_service import UserService
from api.utils import *


@provide_services
@post
def login(request, user_service: UserService = None, **kwargs):
    data = json.loads(request.body)

    login_data = data.get('login', None)
    password_data = data.get('password', None)

    if not (login_data and password_data):
        raise BadRequest('Необходимо заполнить все поля')

    if not user_service.check_credentials(login_data, password_data):
        raise BadRequest('Неверный логин или пароль')

    user = user_service.get_user_by_login(login_data)

    token = user_service.generate_jwt(user)

    return HttpResponse(json.dumps(token), content_type='application/json')


@provide_services
@post
def register(request, user_service: UserService = None, **kwargs):
    data = json.loads(request.body)

    login_data = data.get('login', None)
    password_data = data.get('password', None)
    first_name_data = data.get('first_name', None)
    last_name_data = data.get('last_name', None)
    phone_number_data = data.get('phone_number', None)

    if not (login_data and password_data and first_name_data and last_name_data and phone_number_data):
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
        phone_number=phone_number_data
    )

    if not result:
        raise BadRequest('Не удалось создать пользователя')

    return HttpResponse()


@provide_services
@jwt_secured
@get
def profile(request, user=None, **kwargs):
    return HttpResponse(UserDTO.from_model(user), content_type='application/json')

