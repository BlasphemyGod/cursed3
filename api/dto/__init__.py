import dataclasses
import json
from dataclasses import dataclass

from api.models import User


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass
class UserDTO:
    id: int
    first_name: str
    last_name: str
    phone_number: str
    role_id: int
    role: str

    @staticmethod
    def from_model(user: User) -> 'UserDTO':
        return UserDTO(user.id, user.first_name, user.last_name, user.phone_number, user.role.id, user.role.name)

    def __str__(self) -> str:
        return json.dumps(self, cls=EnhancedJSONEncoder)