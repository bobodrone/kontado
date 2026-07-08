from dataclasses import dataclass
from datetime import datetime
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.file_io import YamlFileManager
from main.models.base import BaseModel
from main.models.line_item import LineItem
from main.services.client import ClientService
from main.services.project import ProjectService
from enum import Enum


class InvoiceStatus(Enum):
    CREATED = "created"
    SENT = "sent"
    PAID = "paid"
    REMINDER = "reminder"
    CLOSED = "closed"

    def to_yaml(self) -> dict:
        status = self.__dict__
        return status


@dataclass(order=True)
class Invoice(BaseModel):
    id: str
    number: int
    client: str
    projects: [str]
    line_items: [str]
    subject: str
    credit: int
    netto_sum: int
    discount: int
    discount_percent: float
    deposit: int
    deposit_vat: int
    deposit_text: str
    vat: int
    total_sum: int
    currency: str
    created: datetime
    created_date: str
    due_date: str
    sent_date: str | bool
    paid_date: str | bool
    reminder_date: str | bool
    status: InvoiceStatus
    our_ref: str
    their_ref: str

    @staticmethod
    def get_defaults():
        return {
            "id": "10-20221023-my_project",
            "number": 0,
            "client": "",
            "projects": [],
            "line_items": [],
            "subject": "Invoice X",
            "credit": 30,
            "netto_sum": 0,
            "discount": 0,
            "discount_percent": 0.0,
            "deposit": 0,
            "deposit_vat": 0,
            "deposit_text": "",
            "vat": 25,
            "total_sum": 0,
            "currency": "SEK",
            "created": datetime.now(),
            "created_date": "",
            "due_date": "",
            "sent_date": "",
            "paid_date": "",
            "reminder_date": "",
            "status": InvoiceStatus.CREATED,
            "our_ref": "",
            "their_ref": "",
        }

    def to_yaml(self) -> dict:
        line_items = [line_item.to_yaml() for line_item in self.line_items]
        invoice = self.__dict__
        invoice["line_items"] = line_items
        invoice["status"] = self.status.value
        invoice["created"] = int(round(invoice["created"].timestamp()))
        return invoice

    @staticmethod
    def from_yaml(invoice_yaml) -> any:
        if not invoice_yaml["created"]:
            created = datetime.now()
        else:
            created = datetime.fromtimestamp(invoice_yaml["created"])

        client_service = ClientService(fetcher=ClientDataFetcher())
        client = client_service.get_client(invoice_yaml["client"])
        project_service = ProjectService(fetcher=ProjectDataFetcher(client))
        projects = project_service.get_projects(
            in_projects=invoice_yaml["projects"], no_cache=True
        )
        line_items = []
        for li in invoice_yaml["line_items"]:
            line_items.append(LineItem.from_yaml(li))
        status = invoice_yaml["status"]
        if "vat" not in invoice_yaml:
            i = 0
        return Invoice(
            id=invoice_yaml["id"],
            number=invoice_yaml["number"],
            client=client.name,
            projects=[p.name for p in projects],
            line_items=line_items,
            subject=invoice_yaml["subject"],
            credit=invoice_yaml["credit"],
            netto_sum=invoice_yaml["netto_sum"],
            discount=invoice_yaml["discount"],
            discount_percent=invoice_yaml["discount_percent"],
            deposit=invoice_yaml["deposit"],
            deposit_vat=invoice_yaml["deposit_vat"],
            deposit_text=invoice_yaml["deposit_text"],
            vat=invoice_yaml["vat"],
            total_sum=invoice_yaml["total_sum"],
            currency=invoice_yaml["currency"],
            created=created,
            created_date=invoice_yaml["created_date"],
            due_date=invoice_yaml["due_date"],
            sent_date=invoice_yaml["sent_date"],
            paid_date=invoice_yaml["paid_date"],
            reminder_date=invoice_yaml["reminder_date"],
            status=status,
            our_ref=invoice_yaml["our_ref"],
            their_ref=invoice_yaml["their_ref"],
        )

    def write_to_file(self, filepath: str):
        yaml_dict = self.to_yaml()
        YamlFileManager.write(filepath, yaml_dict)
