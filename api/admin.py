from django.contrib import admin
from api.models import *


admin.site.register(User)
admin.site.register(Promo)
admin.site.register(Shift)
admin.site.register(Role)
admin.site.register(Table)
admin.site.register(Ingredient)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ProductIngredient)
