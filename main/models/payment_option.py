"""Classes for handle different payment options"""
from dataclasses import dataclass
from main.models.base import BaseModel


@dataclass()
class PaymentOption(BaseModel):
    """Base class for PaymentOption"""

    label: str
    description: str
    type: str

    def to_yaml(self) -> dict:
        payment_options = self.__dict__
        return payment_options


@dataclass()
class SwishPaymentOption(PaymentOption):
    """Class for handle Swish payments"""

    phone_number: str

    def to_yaml(self) -> dict:
        payment_options = self.__dict__
        return payment_options


@dataclass()
class BankGiroPaymentOption(PaymentOption):
    """Class for handle Bankgiro payments"""

    account_number: str

    def to_yaml(self) -> dict:
        payment_options = self.__dict__
        return payment_options


@dataclass()
class BankTransferPaymentOption(PaymentOption):
    """Class for handle Bank transfer payments"""

    account_number: str
    clearing_number: str
    bank: str

    def to_yaml(self) -> dict:
        payment_options = self.__dict__
        return payment_options


@dataclass()
class InternationalBankTransferPaymentOption(PaymentOption):
    """Class for handle international Bank transfer payments"""

    iban: str
    bic_swift: str
    bank: str

    def to_yaml(self) -> dict:
        payment_options = self.__dict__
        return payment_options
