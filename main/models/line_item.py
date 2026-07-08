from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from main.models.base import BaseModel


class LineItemType(Enum):
    SERVICE = "service"
    PRODUCT = "product"

    def to_yaml(self) -> str:
        lite_item_type = self.value
        return lite_item_type


@dataclass
class LineItem(BaseModel):
    client: str
    project: str
    type: LineItemType
    description: str
    nth: float
    unit_price: int
    currency: str
    task: str
    vat: int
    netto: int
    id: str
    created: datetime
    changed: datetime
    invoiced: bool

    def __lt__(self, other):
        return self.created < other.created

    def to_yaml(self) -> dict:
        line_item = self.__dict__
        line_item["created"] = int(round(line_item["created"].timestamp()))
        line_item["changed"] = int(round(line_item["changed"].timestamp()))
        line_item["type"] = line_item["type"].to_yaml()
        return line_item

    @staticmethod
    def get_defaults(client: str):
        return {
            "id": "proj-20221023-0001",
            "client": "Client 242",
            "project": "website",
            "task": "development",
            "type": LineItemType.SERVICE,
            "description": "Website work",
            "nth": 1,
            "unit_price": 100000,
            "currency": "SEK",
            "vat": 25,
            "netto": 100000,
            "invoiced": False,
            "created": datetime.now(),
        }

    @staticmethod
    def from_yaml(line_item_yaml) -> any:
        if not line_item_yaml["created"]:
            created = datetime.now()
        else:
            created = datetime.fromtimestamp(line_item_yaml["created"])
        if not line_item_yaml["changed"]:
            changed = datetime.now()
        else:
            changed = datetime.fromtimestamp(line_item_yaml["changed"])
        line_item_type = LineItemType(line_item_yaml["type"])
        return LineItem(
            client=line_item_yaml["client"],
            project=line_item_yaml["project"],
            type=line_item_type,
            description=line_item_yaml["description"],
            nth=line_item_yaml["nth"],
            unit_price=line_item_yaml["unit_price"],
            currency=line_item_yaml["currency"],
            task=line_item_yaml["task"],
            vat=line_item_yaml["vat"],
            netto=line_item_yaml["netto"],
            id=line_item_yaml["id"],
            invoiced=line_item_yaml["invoiced"]
            if line_item_yaml["invoiced"]
            else False,
            created=created,
            changed=changed,
        )
