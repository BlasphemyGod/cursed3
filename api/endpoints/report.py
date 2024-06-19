import json

from django.core.exceptions import BadRequest
from django.http import HttpResponse

from api.models import User
from api.services.report_service import ReportService
from api.utils import *


@get
@jwt_secured
@for_roles('Официант', 'Курьер')
@provide_services
def get_user_report(request, user: User = None, report_service: ReportService = None, **kwargs):
    report = report_service.generate_user_report(user)

    return HttpResponse(jsonify(report), content_type='application/json')


@get
@jwt_secured
@provide_services
@for_roles('Админ')
def get_product_sales_report(request, report_service: ReportService, **kwargs):
    from_date_data = request.GET.get('from_date')
    to_date_data = request.GET.get('to_date')

    if not from_date_data or not to_date_data:
        raise BadRequest('Необходимо указать даты начала и окончания периода')

    from_date = timify(from_date_data)
    to_date = timify(to_date_data)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Sales from {from_date.day}.{from_date.month}.{from_date.year} to {to_date.day}.{to_date.month}.{to_date.year}.pdf"'

    report_service.generate_product_sales_report(from_date, to_date, response)

    return response


@get
@jwt_secured
@provide_services
@for_roles('Админ')
def get_employees_report(request, report_service: ReportService = None, **kwargs):
    from_date_data = request.GET.get('from_date')
    to_date_data = request.GET.get('to_date')

    if not from_date_data or not to_date_data:
        raise BadRequest('Необходимо указать даты начала и окончания периода')

    from_date = timify(from_date_data)
    to_date = timify(to_date_data)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Employee Report from {from_date.day}.{from_date.month}.{from_date.year} to {to_date.day}.{to_date.month}.{to_date.year}.pdf"'

    report_service.generate_employees_report(from_date, to_date, response)

    return response
