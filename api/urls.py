from api.views import *
from django.urls import path


__all__ = ['urls']

urls = [
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('profile', profile, name='profile'),

    path('tables/available', get_available_tables_by_date, name='get_available_tables_by_date'),
    path('tables', get_tables, name='get_tables'),

    path('promos', get_promos, name='get_promos'),
    path('promos/new', add_promo, name='new_promo'),

    path('menu', get_menu, name='get_menu'),

    path('products', get_products, name='get_products'),
    path('products/new', add_product, name='new_product'),
    path('products/<int:product_id>/edit', edit_product, name='edit_product'),
    path('products/<int:product_id>/delete', delete_product, name='delete_product'),

    path('ingredients', get_all_ingredients, name='get_all_ingredients'),
    path('ingredients/replenish', replenish_ingredients, name='replenish_ingredients'),

    path('book', book_table, name='book_table'),
    path('booking', get_booking, name='get_booking'),
    path('booking/cancel', cancel_booking, name='cancel_booking'),

    path('orders/delivery', get_delivery_orders, name='get_delivery_orders'),
    path('orders/delivery/unfinished', get_unfinished_delivery_orders, name='get_unfinished_delivery_orders'),
    path('orders/delivery/appoint', appoint_courier_to_order, name='appoint_courier_to_order'),

    path('orders/active', get_active_orders, name='get_active_orders'),

    path('orders', get_user_orders, name='get_user_orders'),
    path('orders/new', create_order, name='create_order'),
    path('order/<int:order_id>/status', change_order_status, name='change_order_status'),

    path('orders/analyze', get_analyze, name='get_analyze'),

    path('employees', get_employees, name='get_employees'),
    path('employees/new', new_employee, name='new_employee'),
    path('employee/shift', get_employee_shifts, name='get_employee_shifts'),
    path('employee/roles', get_employees_roles, name='get_employees_roles'),
    path('employee/<int:employee_id>/fire', get_employees_roles, name='fire_employee'),

    path('shifts', get_employees_by_shift, name='get_employees_by_shift'),
    path('shift/appoint', appoint_employee_to_shift, name='appoint_employee_to_shift'),
    path('shift/remove', remove_employee_from_shift, name='remove_employee_from_shift'),
]
