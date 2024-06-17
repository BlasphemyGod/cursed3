from api.views import *
from django.urls import path


__all__ = ['urls']

urls = [
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('profile', profile, name='profile'),

    path('tables/available', get_available_tables_by_date, name='get_available_tables_by_date'),

    path('promos', get_promos, name='get_promos'),

    path('menu', get_menu, name='get_menu'),

    path('book', book_table, name='book_table'),
    path('booking', get_booking, name='get_booking'),
    path('booking/cancel', cancel_booking, name='cancel_booking'),
    path('orders', get_user_orders, name='get_user_orders'),
    path('orders/new', create_order, name='create_order'),
    path('order/<int:order_id>/status', change_order_status, name='change_order_status'),

    path('employees', get_employees, name='get_employees'),
    path('employees/new', new_employee, name='new_employee'),
    path('employee/shift', get_employee_shifts, name='get_employee_shifts'),
    path('employee/roles', get_employees_roles, name='get_employees_roles')
]