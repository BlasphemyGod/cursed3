import datetime

from django.db.models import Q
from jwt import encode, decode, DecodeError

from cursed import settings
from api.models import User, Role
from django.contrib.auth import authenticate


class UserService:
    def generate_jwt(self, user: User) -> str:
        return encode(
            {
                'id': user.id,
                'role_id': user.role_id,
                'exp': datetime.datetime.now() + datetime.timedelta(days=30)
            },
            key=settings.SECRET_KEY
        )

    def check_jwt(self, token: str) -> User | None:
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            return User.objects.get(id=payload['id'])
        except DecodeError:
            return None

    def check_credentials(self, login: str, password: str) -> bool:
        if _ := authenticate(username=login, password=password):
            return True
        return False

    def add_user(
            self,
            login: str,
            password: str,
            first_name: str,
            last_name: str,
            phone_number: str,
            role: Role = None
    ) -> bool:
        if existing_user := User.objects.complex_filter(Q(username=login) | Q(phone_number=phone_number)):
            return False

        if role is None:
            role = Role.objects.get(name__startswith='Клиент')

        new_user = User.objects.create_user(
            username=login,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role=role
        )

        new_user.save()

        return True

    def get_user_by_login(self, login: str) -> User | None:
        try:
            return User.objects.get(username=login)
        except User.DoesNotExist:
            return None

    def check_phone_number(self, phone_number: str) -> bool:
        return not User.objects.filter(phone_number=phone_number).exists()

    def change_user_password(self, user: User, password: str):
        user.set_password(password)

    def get_profile_data(self, token: str) -> User | None:
        return self.check_jwt(token)
