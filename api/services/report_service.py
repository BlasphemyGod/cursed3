from datetime import date, timedelta
from typing import Any

from django.db.models import Sum, F
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from api.models import User, Order, OrderProduct


__all__ = ['ReportService']


pdfmetrics.registerFont(TTFont('Verdana', 'fonts/Verdana.ttf'))
styles = getSampleStyleSheet()
normal = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Verdana')
heading1 = ParagraphStyle('Heading1', parent=styles['Heading1'], fontName='Verdana')
heading2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName='Verdana')
table_style = TableStyle([
    ('GRID', (0, 0), (-1, -1), 1, 'black'),
    ('BACKGROUND', (0, 0), (-1, 0), 'lightgrey'),
    ('FONTNAME', (0, 0), (-1, -1), 'Verdana'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
])


class ReportService:
    def generate_user_report(self, user: User) -> list[dict[str, Any]]:
        today = date.today()
        seven_days_ago = today - timedelta(days=6)

        report_data = []

        for day_offset in range(7):
            current_date = seven_days_ago + timedelta(day_offset)
            orders_for_day = self._get_orders_for_user_and_date(user, current_date)
            report_data.append(
                {
                    'date': f'{current_date.day:02d}.{current_date.month:02d}',
                    'orders': orders_for_day.count(),
                    'total': sum([o.total for o in orders_for_day])
                }
            )

        return report_data

    def _get_orders_for_user_and_date(self, user: User, current_date: date):
        if user.role.name == 'Официант':
            orders_for_day = Order.objects.filter(
                waiter=user,
                date__year=current_date.year,
                date__month=current_date.month,
                date__day=current_date.day
            )
        elif user.role.name == 'Курьер':
            orders_for_day = Order.objects.filter(
                courier=user,
                date__year=current_date.year,
                date__month=current_date.month,
                date__day=current_date.day
            )
        else:
            raise ValueError("Неподдерживаемая роль пользователя")

        return orders_for_day

    def generate_product_sales_report(self, from_date: date, to_date: date, buffer):
        sold_products = OrderProduct.objects.filter(
            order__date__date__gte=from_date,
            order__date__date__lte=to_date
        ).values('product__name', 'product__price').annotate(
            total_quantity=Sum('count'),
            total_price=F('product__price') * F('total_quantity')
        ).order_by('-total_quantity')

        most_popular_product = sold_products.first()
        most_profit_product = sold_products.order_by('-total_price').first()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        story = [
            Paragraph(f"Продажи с {from_date.day:02d}.{from_date.month:02d}.{from_date.year} по {to_date.day:02d}.{to_date.month:02d}.{to_date.year}", heading1),
            Spacer(1, 0.25 * inch)
        ]

        for product in sold_products:
            story.append(Paragraph(f"Название: {product['product__name']}", normal))
            story.append(Paragraph(f"Количество: {product['total_quantity']} шт.", normal))
            story.append(Paragraph(f"Цена: {product['product__price']} р.", normal))
            story.append(Paragraph(f"Общая цена: {product['total_price']} р.", normal))
            story.append(Spacer(1, 0.15 * inch))

        story.append(Paragraph(f"Итого: {sum([p['total_price'] for p in sold_products])} р.", heading2))

        story.append(Paragraph("Популярная позиция меню:", heading2))
        story.append(Paragraph(f"Название: {most_popular_product['product__name']}", normal))
        story.append(Paragraph(f"Количество: {most_popular_product['total_quantity']} шт.", normal))
        story.append(Paragraph(f"Цена: {most_popular_product['product__price']} р.", normal))
        story.append(Paragraph(f"Общая цена: {most_popular_product['total_price']} р.", normal))

        story.append(Spacer(1, 0.15 * inch))

        story.append(Paragraph("Наибольшая выручка:", heading2))
        story.append(Paragraph(f"Название: {most_profit_product['product__name']}", normal))
        story.append(Paragraph(f"Количество: {most_profit_product['total_quantity']} шт.", normal))
        story.append(Paragraph(f"Цена: {most_profit_product['product__price']} р.", normal))
        story.append(Paragraph(f"Общая цена: {most_profit_product['total_price']} р.", normal))

        doc.build(story)
        return buffer

    def generate_employees_report(self, from_date: date, to_date: date, buffer):
        employees = User.objects.filter(role__name__in=['Официант', 'Курьер'])

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = [
            Paragraph(
                f"Отчет по сотрудникам с {from_date.day:02d}.{from_date.month:02d}.{from_date.year} по {to_date.day:02d}.{to_date.month:02d}.{to_date.year}",
                heading1
            ),
            Spacer(1, 0.25 * inch)
        ]

        for employee in employees:
            story.append(Paragraph(f"{employee.last_name} {employee.first_name}", heading2))
            story.append(Paragraph(f"Должность: {employee.role.name}", normal))

            total_orders = Order.objects.filter(
                date__range=(from_date, to_date),
                **(
                    {'waiter': employee} if employee.role.name == 'Официант' else
                    {'courier': employee} if employee.role.name == 'Курьер' else
                    {}
                )
            ).count()
            total_revenue = Order.objects.filter(
                date__range=(from_date, to_date),
                **(
                    {'waiter': employee} if employee.role.name == 'Официант' else
                    {'courier': employee} if employee.role.name == 'Курьер' else
                    {}
                )
            ).aggregate(total=Sum('total'))['total'] or 0
            total_shifts = employee.shifts.filter(date__range=(from_date, to_date)).count()

            story.append(Paragraph(f"Обслужил заказов: {total_orders}", normal))
            story.append(Paragraph(f"Выручка с заказов: {total_revenue} р.", normal))
            story.append(Paragraph(f"Выходов на смену: {total_shifts}", normal))


            story.append(Paragraph("Статистика по дням:", heading2))
            table_data = [['Дата', 'Заказов', 'Выручка']]
            current_date = from_date
            while current_date <= to_date:
                if employee.shifts.filter(date=current_date).exists():
                    daily_orders = Order.objects.filter(
                        date__date=current_date,
                        **(
                            {'waiter': employee} if employee.role.name == 'Официант' else
                            {'courier': employee} if employee.role.name == 'Курьер' else
                            {}
                        )
                    ).count()
                    daily_revenue = Order.objects.filter(
                        date__date=current_date,
                        **(
                            {'waiter': employee} if employee.role.name == 'Официант' else
                            {'courier': employee} if employee.role.name == 'Курьер' else
                            {}
                        )
                    ).aggregate(total=Sum('total'))['total'] or 0
                    table_data.append(
                        [
                            f'{current_date.day:02d}.{current_date.month:02d}.{current_date.year}',
                            daily_orders,
                            f"{daily_revenue} р."
                        ]
                    )
                current_date += timedelta(days=1)

            table = Table(table_data)
            table.setStyle(table_style)
            story.append(table)
            story.append(Spacer(1, 0.5 * inch))

        doc.build(story)
        return buffer
