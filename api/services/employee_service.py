from datetime import date

from api.models import User, Order, Shift, Table, Role


class EmployeeService:
    def get_all_employees(self) -> list[User]:
        return list(User.objects.exclude(role__name='Клиент'))

    def appoint_employee_to_shift(self, employee: User, shift_date: date):
        if employee.role.name == 'Клиент':
            raise ValueError('На смену можно назначить только работника')

        if shift := Shift.objects.get(date=shift_date):
            if not shift.user_set.filter(id=employee.id).exists():
                shift.user_set.add(employee)
                shift.save()
        else:
            shift = Shift(date=shift_date)
            shift.user_set.add(employee)
            shift.save()

    def appoint_courier_to_order(self, courier: User, order: Order):
        if courier.role.name != 'Курьер':
            raise ValueError('На доставку можно назначить только курьера')

        if order.courier:
            raise ValueError('Этим заказом уже занимается другой курьер')

        if not order.address:
            raise ValueError('Назначить курьера можно только на заказ с доставкой')

        order.courier = courier
        order.save()

    def appoint_waiter_to_table(self, waiter: User, table: Table):
        if waiter.role.name != 'Официант':
            raise ValueError('На обслуживание стола можно назначить только официанта')

        table.waiter = waiter
        table.save()

    def get_shifts(self) -> dict[str, list[User]]:
        result = {}
        for shift in Shift.objects.all():
            result[shift.date] = list(shift.user_set.all())

        return result

    def get_waiter_appointments(self) -> dict[int, User]:
        return {table.id: table.waiter for table in Table.objects.all()}

    def get_employees_roles(self) -> list[Role]:
        return list(Role.objects.exclude(name='Клиент').all())
