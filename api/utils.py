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

__all__ = ['jwt_secured', 'post', 'get', 'provide_services']


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
            empoloyee_service=EmployeeService()
        )

    return provide


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
