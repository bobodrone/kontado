from dataclasses import dataclass
from main.models.base import BaseModel


@dataclass(order=True)
class Address(BaseModel):
    co: str
    thoroughfare: str
    premise: str
    postalcode: str
    locality: str
    region: str
    country: str

    def to_yaml(self) -> dict:
        return self.__dict__

    @staticmethod
    def get_defaults(street_no: int):
        return {
            "co": None,
            "thoroughfare": f"My street {street_no}",
            "premise": None,
            "postalcode": "123 45",
            "locality": "My city",
            "region": "My state/region",
            "country": "My country",
        }
