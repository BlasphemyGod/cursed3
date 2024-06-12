import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

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
def get_promos(request, promo_service: PromoService, **kwargs):
    return HttpResponse(
        jsonify(
            [
                PromoDTO.from_model(promo)
                for promo in promo_service.get_all()
            ]
        ),
        content_type='application/json'
    )
