from decimal import Decimal

from api.models import Product, Ingredient, ProductIngredient


class ProductService:
    def get_available_ingredients(self) -> list[Ingredient]:
        return list(Ingredient.objects.filter(count__gt=0).all())

    def replenish_ingredients(self, names: list[str], counts: list[int]) -> None:
        for (name, count) in zip(names, counts):
            if Ingredient.objects.filter(name=name).first is None:
                ingredient = Ingredient.objects.create(name=name, count=0)
            else:
                ingredient = Ingredient.objects.get(name=name)
            ingredient.count += count
            ingredient.save()

    def get_all_ingredients(self) -> list[Ingredient]:
        return list(Ingredient.objects.all())

    def add_product(self, name: str, price: Decimal, ingredients: list[Ingredient], counts: list[int]):
        product = Product(name=name, price=price)

        product.save()

        for (ingredient, quantity) in zip(ingredients, counts):
            ProductIngredient(product=product, ingredient=ingredient, count=quantity).save()

    def edit_product(self, product_id: int, name: str, price: Decimal, ingredients: list[Ingredient], counts: list[int]):
        product = Product.objects.get(id=product_id)
        product.name = name
        product.price = price
        product.save()

        ProductIngredient.objects.filter(product_id=product_id).delete()

        for (ingredient, quantity) in zip(ingredients, counts):
            ProductIngredient(product=product, ingredient=ingredient, quantity=quantity).save()

    def delete_product(self, product_id: int):
        Product.objects.get(id=product_id).delete()

    def get_all_products(self) -> list[Product]:
        return list(Product.objects.all())

    def get_product(self, product_id: int) -> Product | None:
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None
