from django.contrib.auth.models import AbstractUser
from django.db import models


class Promo(models.Model):
    text = models.TextField()
    content = models.ImageField(upload_to='promos/%Y/%m/%d/')


class Shift(models.Model):
    date = models.DateField()

    def __str__(self) -> str:
        return f'{self.date.day:02d}.{self.date.month:02d}.{self.date.year}'


class Role(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    phone_number = models.CharField(max_length=12)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    shifts = models.ManyToManyField(to=Shift)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} | {self.role.name}'


class Table(models.Model):
    client = models.ForeignKey(User, related_name='tables', on_delete=models.SET_NULL, null=True, blank=True)
    waiter = models.ForeignKey(User, related_name='assigns', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f'Столик №{self.id}'


class Ingredient(models.Model):
    name = models.CharField(max_length=40)
    count = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.name} | Осталось: {self.count}'


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)

    ingredients = models.ManyToManyField(to=Ingredient, through='ProductIngredient')

    def __str__(self) -> str:
        return f'{self.name} | Цена: {float(self.price)}'


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    count = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.product.name} | {self.ingredient.name}x{self.count}'


class Order(models.Model):
    status = models.CharField(max_length=20)
    date = models.DateTimeField()
    address = models.CharField(max_length=100, null=True, default=None, blank=True)
    client = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    courier = models.ForeignKey(User, related_name='deliveries', on_delete=models.SET_NULL, null=True, default=None, blank=True)

    products = models.ManyToManyField(to=Product, through='OrderProduct')

    def __str__(self) -> str:
        if self.products.exists():
            return f'Заказ №{self.id} от {self.date.day:02d}.{self.date.month:02d}.{self.date.year} в {self.date.hour:02d}:{self.date.minute}' + (' | Отменён' if self.status == 'Отменён' else '')
        else:
            return f'Бронь на {self.date.day:02d}.{self.date.month:02d}.{self.date.year}' + (' | Отменена' if self.status == 'Отменён' else '')  


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    count = models.IntegerField()
