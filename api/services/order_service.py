from collections import defaultdict
from datetime import datetime, date

from api.models import Order, Table, User, Product, OrderProduct, ProductIngredient


class OrderService:
    def change_order_status(self, order: Order, status: str):
        if order.status == 'Обслужен':
            order.table.client = None

        order.status = status
        order.save()

    def cancel_order(self, order: Order) -> bool:
        order.status = 'Отменён'
        order.save()

    def create_order(
            self,
            client: User,
            table: Table | None,
            address: str | None,
            products: list[tuple[Product, int]]
    ) -> Order:
        if not (table or address):
            raise ValueError('Необходимо указать хотя бы один из аргументов: стол или адрес')

        
        if table is not None:
            if not table.waiter:
                raise ValueError('Этот столик не обслуживает ни один официант')

            table.client = client
            table.save()

        order = Order(status='Принят', date=datetime.now(), client=client, table=table, address=address)
        order.save()

        for product, count in products:
            for consumption in ProductIngredient.objects.filter(product=product):
                ingredients_consumption = consumption.count * count

                if consumption.ingredient.count < ingredients_consumption:
                    raise ValueError(f'Недостаточно продуктов на складе для: {product.name}')

                consumption.ingredient.count -= ingredients_consumption

                consumption.ingredient.save()
            
            OrderProduct.objects.create(order=order, product=product, count=count)

        return order

    def get_orders(self, with_status: str | None, with_tables: list[int]) -> list[Order]:
        orders = Order.objects

        if with_status:
            orders = orders.filter(status=with_status)

        if with_tables:
            orders = orders.filter(table__id__in=with_tables)

        return list(filter(lambda o: o.products.exists(), orders.order_by('-date').all()))

    def book_table(self, client: User, time: datetime, table: Table):
        if any(
            list(
                map(
                    lambda o: not o.products.exists(),
                    Order.objects.filter(date__day=time.day, date__month=time.month, date__year=time.year, table=table).exclude(status='Отменён')
                )
            ) + list(
                map(
                    lambda o: not o.products.exists(),
                    Order.objects.filter(date__gte=time, client_id=client.id).exclude(status='Отменён')
                )
            )
        ):
            raise ValueError('Столик уже забронирован')

        order = Order(status='Принят', date=time, client=client, table=table)
        order.save()

    def get_all_bookings(self) -> list[Order]:
        result = []

        for order in Order.objects.all():
            if not order.products.exists():
                result.append(order)

        return result

    def get_available_tables(self, time: date) -> list[Table]:
        result = []

        current_date = date.today()

        tables = Table.objects.all()

        if current_date == date:
            tables = tables.filter(client=None)

        booked_tables = list(
            map(
                lambda order: order.table.id,
                filter(
                    lambda o: not o.products.exists(),
                    Order.objects.filter(date__day=time.day, date__month=time.month, date__year=time.year)
                )
            )
        )

        for table in tables:
            if table.id not in booked_tables:
                result.append(table)

        return result

    def get_user_booking(self, client: User) -> Order | None:
        orders = Order.objects.filter(client=client, date__gte=date.today()).exclude(status='Отменён')
        orders = filter(lambda order: not order.products.exists(), orders)

        return next(iter(orders), None)

    def get_order(self, order_id: int) -> Order:
        return Order.objects.get(id=order_id)

    def get_delivery_orders(self) -> list[Order]:
        return list(Order.objects.filter(status='Передан на доставку').exclude(courier=None).all())

    def get_unfinished_delivery_orders(self) -> list[Order]:
        return list(Order.objects.filter(courier=None).all())

    def analyze_sales(self, from_date: date, to_date: date) -> dict[Product, int]:
        orders = Order.objects.filter(date__gte=from_date).filter(date__lte=to_date)

        result = defaultdict(int)

        for order in orders:
            for position in OrderProduct.objects.filter(order=order):
                result[position] += position.count

        return result
