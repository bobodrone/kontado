from dataclasses import dataclass
from main.models.base import BaseModel


@dataclass(order=True)
class Rate(BaseModel):
    amount: int
    currency: str
    type: str
    vat: int

    @staticmethod
    def get_defaults(amount: int = 0, vat: int = 0):
        return {"amount": amount, "currency": "SEK", "type": "hourly", "vat": vat}
