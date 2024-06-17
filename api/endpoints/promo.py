import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django import forms

from api.dto import PromoDTO
from api.models import Promo
from api.services.employee_service import EmployeeService
from api.services.promo_service import PromoService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент')
@provide_services
def get_promos(request, promo_service: PromoService = None, **kwargs):
    return HttpResponse(
        jsonify(
            [
                PromoDTO.from_model(promo)
                for promo in promo_service.get_all()
            ]
        ),
        content_type='application/json'
    )


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def add_promo(request, promo_service: PromoService = None, **kwargs):
    class NewPromo(forms.Form):
        text = forms.CharField()
        content = forms.ImageField()

    new_promo = NewPromo(request.POST, request.FILES)

    text = new_promo.cleaned_data.get('text')
    img = new_promo.cleaned_data.get('content')

    promo_service.add(text, img)

    return HttpResponse()


@post
@jwt_secured
@for_roles('Админ')
@provide_services
def delete_promo(request, promo_id: int, promo_service: PromoService = None, **kwargs):
    promo_service.delete(promo_id)

    return HttpResponse()
