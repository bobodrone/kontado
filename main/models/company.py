"""Module handle Company data class"""
from dataclasses import dataclass
from datetime import datetime

from main.models.company_info import CompanyInfo
from main.models.contact import Contact
from main.models.base import BaseModel


@dataclass(order=True)
class Company(BaseModel):
    """Class handle Company"""

    name: str
    label: str
    description: str
    company_info: CompanyInfo
    contacts: [Contact]
    created: datetime
    changed: datetime
    language: str

    @staticmethod
    def get_defaults():
        return {
            "name": "company_name",
            "label": "Company name",
            "description": "This is a cool company",
            "company_info": CompanyInfo.get_defaults(),
            "contacts": [Contact.get_defaults()],
            "language": "sv",
        }
