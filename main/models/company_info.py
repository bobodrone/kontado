from dataclasses import dataclass
from main.models.base import BaseModel
from main.models.address import Address


@dataclass(order=True)
class CompanyInfo(BaseModel):
    name: str
    orgnr: str
    vatnr: str
    postal_address: Address
    visitor_address: Address

    def to_yaml(self) -> dict:
        postal_address = self.postal_address.to_yaml()
        visitor_address = self.visitor_address.to_yaml()
        company_info = self.__dict__
        company_info["postal_address"] = postal_address
        company_info["visitor_address"] = visitor_address
        return company_info

    @staticmethod
    def get_defaults():
        return {
            "name": "Company name",
            "orgnr": "123456-7890",
            "vatnr": "SE123456789001",
            "postal_address": Address.get_defaults(69),
            "visitor_address": Address.get_defaults(242),
        }
