from dataclasses import dataclass
from datetime import datetime
from main.models.address import Address
from main.models.company import Company
from main.models.company_info import CompanyInfo
from main.models.contact import Contact


@dataclass
class Client(Company):
    invoice_emails: [str]
    last_invoice: int
    currency: str

    @staticmethod
    def get_defaults():
        return super(Client, Client).get_defaults() | {
            "invoice_emails": [],
            "last_invoice": 0,
            "currency": "SEK",
        }

    def to_yaml(self) -> dict:
        company_info = self.company_info.to_yaml()
        contacts = [contact.to_yaml() for contact in self.contacts]
        client = self.__dict__
        client["company_info"] = company_info
        client["contacts"] = contacts

        return client

    @staticmethod
    def from_yaml(client_yaml) -> any:
        def get_contact(yaml_data):
            return Contact(
                person=yaml_data["person"],
                title=yaml_data["title"],
                email=yaml_data["email"],
                phone=yaml_data["phone"],
            )

        if not client_yaml["created"]:
            created = datetime.now()
        else:
            created = datetime.fromtimestamp(client_yaml["created"])
        if not client_yaml["changed"]:
            changed = datetime.now()
        else:
            changed = datetime.fromtimestamp(client_yaml["changed"])

        contacts = list(map(get_contact, client_yaml["contacts"]))

        return Client(
            name=client_yaml["name"],
            label=client_yaml["label"],
            language=client_yaml["language"],
            description=client_yaml["description"],
            company_info=CompanyInfo(
                name=client_yaml["company_info"]["name"],
                orgnr=client_yaml["company_info"]["orgnr"],
                vatnr=client_yaml["company_info"]["vatnr"],
                postal_address=Address(
                    co=client_yaml["company_info"]["postal_address"]["co"],
                    thoroughfare=client_yaml["company_info"]["postal_address"][
                        "thoroughfare"
                    ],
                    premise=client_yaml["company_info"]["postal_address"]["premise"],
                    postalcode=client_yaml["company_info"]["postal_address"][
                        "postalcode"
                    ],
                    locality=client_yaml["company_info"]["postal_address"]["locality"],
                    region=client_yaml["company_info"]["postal_address"]["region"],
                    country=client_yaml["company_info"]["postal_address"]["country"],
                ),
                visitor_address=Address(
                    co=client_yaml["company_info"]["visitor_address"]["co"],
                    thoroughfare=client_yaml["company_info"]["visitor_address"][
                        "thoroughfare"
                    ],
                    premise=client_yaml["company_info"]["visitor_address"]["premise"],
                    postalcode=client_yaml["company_info"]["visitor_address"][
                        "postalcode"
                    ],
                    locality=client_yaml["company_info"]["visitor_address"]["locality"],
                    region=client_yaml["company_info"]["visitor_address"]["region"],
                    country=client_yaml["company_info"]["visitor_address"]["country"],
                ),
            ),
            contacts=contacts,
            last_invoice=0,
            invoice_emails=[],
            currency="SEK",
            created=created,
            changed=changed,
        )
