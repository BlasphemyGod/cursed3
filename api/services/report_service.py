from datetime import date, timedelta
from typing import Any

from django.db.models import Count, Sum
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from api.models import User, Order, OrderProduct


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
                    'date': f'{current_date.day}.{current_date.month}',
                    'orders': orders_for_day.count(),
                    'total': orders_for_day.aggregate(total_sum=Sum('total'))['total_sum'] or 0
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
            total_price='product__price * count'
        ).order_by('-total_quantity')

        most_popular_product = sold_products.first()

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        styles['Normal'] = ParagraphStyle('Normal', parent=styles['Normal'], fontName='Verdana')
        story = [
            Paragraph(f"Отчет о продажах с {from_date.day}.{from_date.month}.{from_date.year} по {to_date.day}.{to_date.month}.{to_date.year}", styles['Heading1']),
            Spacer(1, 0.25 * inch)
        ]

        for product in sold_products:
            story.append(Paragraph(f"Название: {product['product__name']}", styles['Normal']))
            story.append(Paragraph(f"Количество: {product['total_quantity']}", styles['Normal']))
            story.append(Paragraph(f"Цена: {product['product__price']}", styles['Normal']))
            story.append(Paragraph(f"Общая цена: {product['total_price']}", styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        story.append(Paragraph("Популярная позиция меню:", styles['Heading2']))
        story.append(Paragraph(f"Название: {most_popular_product['product__name']}", styles['Normal']))
        story.append(Paragraph(f"Количество: {most_popular_product['total_quantity']}", styles['Normal']))

        doc.build(story)
        return buffer
