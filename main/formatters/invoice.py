""" Client formatters"""
from datetime import datetime

from .formatters import TableFormatter
from ..models.invoice import Invoice


class InvoiceListTableFormatter(TableFormatter):
    """Class Invoice formatter"""

    def __init__(
        self,
        title: str,
        settings: dict = None,
    ):
        super().__init__(settings)
        self.create_table(title=title, show_lines=True)

    def format_table(self, data: [Invoice]):
        self.table.add_column("No", style="cyan")
        self.table.add_column("Date")
        self.table.add_column("Client")
        self.table.add_column("Projects")
        self.table.add_column("Line items")
        self.table.add_column("Net")
        self.table.add_column("VAT")
        self.table.add_column("Gross")
        self.table.add_column("Status")

        for invoice in data:
            projects = [project for project in invoice.projects]
            line_items = [item.description for item in invoice.line_items]
            dates = []
            dates.append(f"C: {invoice.created_date}")
            if invoice.sent_date:
                dates.append(f"S: {invoice.sent_date}")
            dates.append(f"D: {invoice.due_date}")
            if invoice.reminder_date:
                dates.append(f"R: {invoice.reminder_date}")
            if invoice.paid_date:
                dates.append(f"P: {invoice.paid_date}")

            self.table.add_row(
                f"{invoice.number}",
                "\n".join(dates),
                invoice.client,
                "\n".join(projects),
                "\n".join(line_items),
                f"{invoice.netto_sum/100: {'8,.2f'}} {invoice.currency}",
                f"{invoice.vat/100: {'8,.2f'}} {invoice.currency}",
                f"{invoice.total_sum/100: {'8,.2f'}} {invoice.currency}",
                f"{invoice.status}",
            )
