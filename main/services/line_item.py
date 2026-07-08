import copy
from datetime import datetime, date
from enum import Enum
from typing import List, Tuple

from main.fetchers.data_fetcher import DataFetcher
from main.models.client import Client
from main.models.project import Project
from main.services.service import Service
from main.models.line_item import LineItem, LineItemType


class LineItemSorting(Enum):
    ASC = "asc"
    DESC = "desc"

    def to_yaml(self) -> dict:
        sorting = self.__dict__
        return sorting


class LineItemService(Service):
    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher

    def get_line_items(
        self,
        client: Client = None,
        project: Project = None,
        exclude_invoiced: bool = True,
        in_line_items: List = None,
        sort_by: LineItemSorting = LineItemSorting.ASC,
    ):
        line_items = self.fetcher.read_data()
        if line_items:
            if client or project or exclude_invoiced:
                filtered = line_items
                if in_line_items:
                    filtered = filter(lambda item: item.client == client, filtered)
                if client:
                    filtered = filter(lambda item: item.client == client.name, filtered)
                if project:
                    filtered = filter(
                        lambda item: item.project == project.name, filtered
                    )
                if exclude_invoiced:
                    filtered = filter(lambda item: item.invoiced is False, filtered)
                line_items = list(filtered)
                line_items.sort()
                return line_items
            else:
                line_items.sort()
                return line_items
        return []

    def create_line_item(
        self,
        client: str,
        project: str,
        type: str,
        description: str,
        nth: float,
        unit_price: int,
        task: str,
        vat: int,
        currency: str,
        created: datetime = None,
    ) -> Tuple[str, LineItem]:
        line_item_path = self.fetcher.get_line_items_path()
        if not created:
            created = datetime.now()
            created_at = date.today().strftime("%Y%m%d")
        else:
            created_at = datetime.fromtimestamp(created).strftime("%Y%m%d")
        next_num = self.fetcher.get_next_num(created_at)
        line_item_name = f"{self.fetcher.client.name}-{project}-{created_at}-{next_num}"

        line_item_data = LineItem(
            id=line_item_name,
            currency=currency,
            client=client,
            project=project,
            type=LineItemType(type),
            description=description,
            nth=nth,
            unit_price=unit_price,
            task=task,
            vat=vat,
            netto=int(nth * unit_price),
            created=created,
            changed=created,
            invoiced=False,
        )
        line_item_handle = self.fetcher.join_path(
            [line_item_path, f"{line_item_name}.yml"]
        )
        copy.deepcopy(line_item_data).write_to_file(line_item_handle)
        return line_item_handle, line_item_data
