import dataclasses
import json
from datetime import datetime, date
from functools import wraps

from api.models import User
from django.core.exceptions import PermissionDenied

import jwt
from django.http import HttpResponse

from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.product_service import ProductService
from api.services.promo_service import PromoService
from api.services.user_service import UserService
from cursed import settings

__all__ = ['jwt_secured', 'post', 'get', 'provide_services', 'for_roles', 'jsonify', 'timify']


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, date):
            return f'{o.day}.{o.month}.{o.year}'
        if isinstance(o, datetime):
            return f'{o.day}.{o.month}.{o.year} {o.hour}:{o.minute}'
        return super().default(o)


def timify(time):
    if not time:
        time = datetime.datetime.now()
    else:
        date = time.split()[0]
        day, month, year = date.split('-')

        time = time.split()[1]
        hour, minute = time.split(':')

        time = datetime(int(year), int(month), int(day), int(hour), int(minute))


def jsonify(obj):
    return json.dumps(obj, cls=EnhancedJSONEncoder)


def jwt_secured(endpoint):
    @wraps(endpoint)
    def is_authenticated(request, *args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth is None:
            raise PermissionDenied
        token = auth.split()[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('id')

            user = User.objects.get(id=user_id)

            if user is None:
                raise PermissionDenied('Invalid token')

        except jwt.ExpiredSignatureError:
            raise PermissionDenied('Token has expired')

        return endpoint(request, *args, **kwargs, user=user, token=token)

    return is_authenticated


def provide_services(endpoint):
    @wraps(endpoint)
    def provide(request, *args, **kwargs):
        return endpoint(
            request,
            *args,
            **kwargs,
            user_service=UserService(),
            promo_service=PromoService(),
            product_service=ProductService(),
            order_service=OrderService(),
            employee_service=EmployeeService()
        )

    return provide


def for_roles(*roles: str):
    def for_roles_decorator(endpoint):
        @wraps(endpoint)
        def validator(request, *args, **kwargs):
            if kwargs.get('user').role.name not in roles:
                raise PermissionDenied('У вас нет таких прав')

            return endpoint(request, *args, **kwargs)

        return validator

    return for_roles_decorator


def post(endpoint):
    @wraps(endpoint)
    def is_post(request, *args, **kwargs):
        if request.method == 'POST':
            return endpoint(request, *args, **kwargs)

        return HttpResponse(status=405)

    return is_post


def get(endpoint):
    @wraps(endpoint)
    def is_get(request, *args, **kwargs):
        if request.method == 'GET':
            return endpoint(request, *args, **kwargs)

        return HttpResponse(status=405)

    return is_get
