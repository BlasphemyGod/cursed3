import dataclasses
import json
from datetime import datetime, date, timedelta
from functools import wraps
from decimal import Decimal

from api.models import User
from django.core.exceptions import PermissionDenied

import jwt
from django.http import HttpResponse

from api.services.employee_service import EmployeeService
from api.services.order_service import OrderService
from api.services.product_service import ProductService
from api.services.promo_service import PromoService
from api.services.report_service import ReportService
from api.services.user_service import UserService
from cursed import settings

__all__ = ['jwt_secured', 'post', 'get', 'provide_services', 'for_roles', 'jsonify', 'timify']


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime):
            o = o + timedelta(hours=4)
            return f'{o.day:02d}.{o.month:02d}.{o.year} {o.hour:02d}:{o.minute:02d}'
        if isinstance(o, date):
            return f'{o.day:02d}.{o.month:02d}.{o.year}'
        if isinstance(o, Decimal):
            return float(o)

        return super().default(o)


def timify(time):
    if not time:
        real_time = datetime.now()
    else:
        date = time.split()[0]
        day, month, year = date.split('.')

        hour = minute = 0

        if len(time.split()) == 2:
            time = time.split()[1]
            hour, minute = time.split(':')

        real_time = datetime(int(year), int(month), int(day), int(hour), int(minute))

    return real_time


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
            employee_service=EmployeeService(),
            report_service=ReportService()
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
        if request.method == 'OPTIONS':
            return HttpResponse(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": request.headers['origin'],
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                    "Access-Control-Max-Age": 86400 ,
                    "Vary": "Accept-Encoding, Origin"
                }
            )
        if request.method == 'POST':
            response = endpoint(request, *args, **kwargs)
            if 'origin' in request.headers:
                response.headers["Access-Control-Allow-Origin"] = request.headers['origin']

            return response

        return HttpResponse(status=405)

    return is_post


def get(endpoint):
    @wraps(endpoint)
    def is_get(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return HttpResponse(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": request.headers['origin'],
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                    "Access-Control-Max-Age": 86400,
                    "Vary": "Accept-Encoding, Origin"
                }
            )

        if request.method == 'GET':
            response = endpoint(request, *args, **kwargs)
            if 'origin' in request.headers:
                response.headers["Access-Control-Allow-Origin"] = request.headers['origin']

            return response

        return HttpResponse(status=405)

    return is_get
