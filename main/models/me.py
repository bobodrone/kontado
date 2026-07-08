from dataclasses import dataclass
from datetime import datetime

from main.models.address import Address
from main.models.company import Company
from main.models.company_info import CompanyInfo
from main.models.contact import Contact
from main.models.payment_option import (
    PaymentOption,
    BankGiroPaymentOption,
    SwishPaymentOption,
    InternationalBankTransferPaymentOption,
    BankTransferPaymentOption,
)


@dataclass(order=True)
class Me(Company):
    last_invoice: int
    payment_options: [PaymentOption]

    def to_yaml(self) -> dict:
        company_info = self.company_info.to_yaml()
        contacts = [contact.to_yaml() for contact in self.contacts]
        payment_options = [
            payment_option.to_yaml() for payment_option in self.payment_options
        ]
        me = self.__dict__
        me["company_info"] = company_info
        me["payment_options"] = payment_options
        me["contacts"] = contacts
        return me

    @staticmethod
    def get_defaults():
        return super(Me, Me).get_defaults() | {"last_invoice": 0, "payment_options": []}

    @staticmethod
    def from_yaml(me_yaml) -> any:
        if not me_yaml["created"]:
            created = datetime.now()
        else:
            created = datetime.fromtimestamp(me_yaml["created"])
        if not me_yaml["changed"]:
            changed = datetime.now()
        else:
            changed = datetime.fromtimestamp(me_yaml["changed"])

        def get_contact(yaml_data):
            return Contact(
                person=yaml_data["person"],
                title=yaml_data["title"],
                email=yaml_data["email"],
                phone=yaml_data["phone"],
            )

        contacts = list(map(get_contact, me_yaml["contacts"]))

        def get_payment_options(yaml_data):
            if yaml_data["type"] == "bankgiro":
                return BankGiroPaymentOption(
                    label="Bankgiro",
                    description="B2B fund transfer system (only works in Sweden)",
                    type="bankgiro",
                    account_number=yaml_data["account_number"],
                )
            elif yaml_data["type"] == "bankaccount":
                return BankTransferPaymentOption(
                    label="Bank tranfser",
                    description="Swedish bank transfer (only works in Sweden)",
                    type="banktransfer",
                    clearing_number=yaml_data["clearing_number"],
                    account_number=yaml_data["account_number"],
                    bank=yaml_data["bank"],
                )
            elif yaml_data["type"] == "banktransfer":
                return InternationalBankTransferPaymentOption(
                    label="Bank transfer",
                    description="International bank transfer",
                    type="banktransfer",
                    iban=yaml_data["iban"],
                    bic_swift=yaml_data["bic_swift"],
                    bank=yaml_data["bank"],
                )
            elif yaml_data["type"] == "swish":
                return SwishPaymentOption(
                    label="Swish",
                    description="Smart phone transfer (only works in Sweden)",
                    type="swish",
                    phone_number="+46707222269",
                )

        payment_options = list(map(get_payment_options, me_yaml["payment_options"]))

        return Me(
            name=me_yaml["name"],
            label=me_yaml["label"],
            language=me_yaml["language"],
            description=me_yaml["description"],
            contacts=contacts,
            company_info=CompanyInfo(
                name=me_yaml["company_info"]["name"],
                orgnr=me_yaml["company_info"]["orgnr"],
                vatnr=me_yaml["company_info"]["vatnr"],
                postal_address=Address(
                    co=me_yaml["company_info"]["postal_address"]["co"],
                    thoroughfare=me_yaml["company_info"]["postal_address"][
                        "thoroughfare"
                    ],
                    premise=me_yaml["company_info"]["postal_address"]["premise"],
                    postalcode=me_yaml["company_info"]["postal_address"]["postalcode"],
                    locality=me_yaml["company_info"]["postal_address"]["locality"],
                    region=me_yaml["company_info"]["postal_address"]["region"],
                    country=me_yaml["company_info"]["postal_address"]["country"],
                ),
                visitor_address=Address(
                    co=me_yaml["company_info"]["visitor_address"]["co"],
                    thoroughfare=me_yaml["company_info"]["visitor_address"][
                        "thoroughfare"
                    ],
                    premise=me_yaml["company_info"]["visitor_address"]["premise"],
                    postalcode=me_yaml["company_info"]["visitor_address"]["postalcode"],
                    locality=me_yaml["company_info"]["visitor_address"]["locality"],
                    region=me_yaml["company_info"]["visitor_address"]["region"],
                    country=me_yaml["company_info"]["visitor_address"]["country"],
                ),
            ),
            last_invoice=me_yaml["last_invoice"],
            created=created,
            changed=changed,
            payment_options=payment_options,
        )
