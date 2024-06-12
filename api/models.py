from django.contrib.auth.models import AbstractUser
from django.db import models


class Promo(models.Model):
    text = models.TextField()
    content = models.ImageField(upload_to='promos/%Y/%m/%d/')


class Shift(models.Model):
    date = models.DateField()


class Role(models.Model):
    name = models.CharField(max_length=20)


class User(AbstractUser):
    phone_number = models.CharField(max_length=12)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    shifts = models.ManyToManyField(to=Shift, blank=True)


class Table(models.Model):
    client = models.ForeignKey(User, related_name='tables', on_delete=models.SET_NULL, null=True)
    waiter = models.ForeignKey(User, related_name='assigns', on_delete=models.SET_NULL, null=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=40)
    count = models.IntegerField()


class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=11, decimal_places=2)

    ingredients = models.ManyToManyField(to=Ingredient, through='ProductIngredient')


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    count = models.IntegerField()


class Order(models.Model):
    status = models.CharField(max_length=20)
    date = models.DateTimeField()
    address = models.CharField(max_length=100, null=True, default=None)
    client = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, default=None)
    courier = models.ForeignKey(User, related_name='deliveries', on_delete=models.SET_NULL, null=True, default=None)

    products = models.ManyToManyField(to=Product, through='OrderProduct')


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    count = models.IntegerField()
