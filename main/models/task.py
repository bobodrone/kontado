from dataclasses import dataclass
from main.models.base import BaseModel
from main.models.rate import Rate


@dataclass(order=True)
class Task(BaseModel):
    type: str
    label: str
    default: bool
    rate: Rate

    @staticmethod
    def get_defaults(amount: int, vat: int):
        return [
            {
                "type": "development",
                "label": "Development",
                "default": True,
                "rate": Rate.get_defaults(amount, vat),
            },
            {
                "type": "development_free",
                "label": "Development (free)",
                "default": False,
                "rate": Rate.get_defaults(),
            },
            {
                "type": "administration",
                "label": "Administration",
                "default": False,
                "rate": Rate.get_defaults(amount, vat),
            },
            {
                "type": "administration_free",
                "label": "Administration (free)",
                "default": False,
                "rate": Rate.get_defaults(),
            },
        ]
