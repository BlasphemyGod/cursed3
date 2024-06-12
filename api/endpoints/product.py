import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.dto import EmployeeDTO, UserDTO, ProductDTO
from api.models import Role, Table
from api.services.employee_service import EmployeeService
from api.services.product_service import ProductService
from api.services.user_service import UserService
from api.utils import *


@get
@jwt_secured
@for_roles('Клиент', 'Официант')
@provide_services
def get_menu(request, product_service: ProductService, **kwargs):
    return HttpResponse(
        jsonify(
            [
                ProductDTO.from_model(p)
                for p in product_service.get_all_products()
            ]
        )
    )