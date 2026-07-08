""" Client formatters"""
from datetime import datetime
from .formatters import TableFormatter
from ..models.line_item import LineItem


class LineItemListTableFormatter(TableFormatter):
    """Class LineItem formatter"""

    def format_table(self, data: [LineItem]):
        self.table.add_column("No", style="cyan")
        self.table.add_column("Client")
        self.table.add_column("Project")
        self.table.add_column("Date")
        self.table.add_column("Description")
        self.table.add_column("Nth")
        self.table.add_column("Unit price")
        self.table.add_column("Currency")
        self.table.add_column("Netto")
        self.table.add_column("Vat")

        index = 0
        for item in data:
            index = index + 1
            vat = 0
            if item.vat:
                vat = item.nth * item.unit_price * (item.vat / 100)
            item_created = item.created.strftime("%Y-%m-%d")

            self.table.add_row(
                f"{index}",
                f"{item.client}",
                f"{item.project}",
                f"{item_created}",
                f"{item.description}",
                f"{item.nth}",
                f"{item.unit_price / 100: {'8,.2f'}}",
                f"{item.currency}",
                f"{item.netto / 100: {'8,.2f'}}",
                f"{vat / 100:{'8,.2f' if vat > 0 else ''}}",
            )


class LineItemListGroupedTableFormatter(TableFormatter):
    """Class LineItem formatter"""

    def format_table(self, data: [LineItem]):
        self.table.add_column("No", style="cyan")
        self.table.add_column("Client")
        self.table.add_column("Project")
        self.table.add_column("Date")
        self.table.add_column("Description")
        self.table.add_column("Nth")
        self.table.add_column("Unit price")
        self.table.add_column("Currency")
        self.table.add_column("Netto")
        self.table.add_column("Vat")

        index = 0
        for project in data:
            for service in data[project]:
                for currency in data[project][service]:
                    for item_price in data[project][service][currency]:
                        items = list(data[project][service][currency][item_price])
                        items.sort()
                        for item in items:
                            index = index + 1
                            vat = 0
                            if item.vat:
                                vat = item.nth * item.unit_price * (item.vat / 100)
                            item_created = item.created.strftime("%Y-%m-%d")

                            self.table.add_row(
                                f"{index}",
                                f"{item.client}",
                                f"{item.project}",
                                f"{item_created}",
                                f"{item.description}",
                                f"{item.nth}",
                                f"{item.unit_price / 100: {'8,.2f'}}",
                                f"{item.currency}",
                                f"{item.netto / 100: {'8,.2f'}}",
                                f"{vat / 100:{'8,.2f' if vat > 0 else ''}}",
                            )
        if self.settings:
            self.table.add_section()
            self.table.add_row(
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "S:a",
                f"{self.settings['sums']['netto_sum'] / 100: {'8,.2f'}}",
                f"{self.settings['sums']['vat'] / 100: {'8,.2f'}}",
            )
