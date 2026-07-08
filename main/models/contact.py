from dataclasses import dataclass
from main.models.base import BaseModel


@dataclass(order=True)
class Contact(BaseModel):
    person: str
    title: str
    email: str
    phone: str

    @staticmethod
    def get_defaults():
        return {
            "person": "Kenny Bräck",
            "title": "Race Driver",
            "email": "kenny@brack.com",
            "phone": "+46 700 12 34 56",
        }
