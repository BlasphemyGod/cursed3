from api.models import Promo


class PromoService:
    def add(self, text: str, content):
        Promo(text=text, content=content).save()

    def get_last(self) -> Promo:
        return Promo.objects.last()

    def get_all(self) -> list[Promo]:
        return Promo.objects.order_by('-id').all()

    def edit(self, promo_id: int, text: str, content: bytes):
        if promo := Promo.objects.get(id=promo_id):
            promo.text = text
            promo.content = content
            promo.save()
        else:
            raise ValueError(f'Promo with such id doesn\'t exists')

    def delete(self, promo_id: int):
        Promo.objects.get(id=promo_id).delete()
