# -*- coding: utf-8 -*-
import os
from datetime import datetime, date, timedelta
from config import settings
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.line_item_data_fetcher import LineItemDataFetcher
from main.fetchers.me_data_fetcher import MeDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FileIO, FileManager
from main.inputs.invoice import InvoiceInput
from main.models.invoice import Invoice, InvoiceStatus
from main.generate import generate
from main.models.client import Client
from main.models.line_item import LineItem
from main.models.project import Project
from main.services.client import ClientService
from main.services.line_item import LineItemService
from main.services.me import MeService
from main.services.project import ProjectService
from main.services.service import Service


class InvoiceService(Service):
    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher

    def get_invoices(self, status: InvoiceStatus = None) -> [Invoice]:
        invoices = self.fetcher.read_data()
        if status is not None:
            return list(
                filter(
                    lambda invoice: invoice.status == status.value,
                    sorted(invoices, key=lambda x: x.number),
                )
            )

        return sorted(invoices, key=lambda x: x.number)

    def collect_line_items(self, client: Client, projects: [Project]) -> [LineItem]:
        collected_line_items = []
        for project in projects:
            line_item_service = LineItemService(
                fetcher=LineItemDataFetcher(client, project)
            )
            items = line_item_service.get_line_items(
                client=client, project=project, exclude_invoiced=True
            )
            if items:
                collected_line_items.extend(items)
        return collected_line_items

    def collect_grouped_line_items(
        self, client: Client, projects: [Project]
    ) -> [LineItem]:
        collected_line_items = {}
        for project in projects:
            line_item_service = LineItemService(
                fetcher=LineItemDataFetcher(client, project)
            )
            items = line_item_service.get_line_items(
                client=client, project=project, exclude_invoiced=True
            )
            if items:
                # group by currency and then group by item_price
                grouped = {}
                for item in items:
                    if item.type not in grouped.keys():
                        grouped[item.type] = {}
                    if item.currency not in grouped[item.type].keys():
                        grouped[item.type][item.currency] = {}
                    if item.unit_price not in grouped[item.type][item.currency].keys():
                        grouped[item.type][item.currency][item.unit_price] = []
                    grouped[item.type][item.currency][item.unit_price].append(item)
                collected_line_items[project.name] = grouped
        return collected_line_items

    @staticmethod
    def sum_collected_lite_items(cl_items):
        """ "The goal here is to only return as many line items there is projects"""
        """Or unique type, currency, or unit_price"""
        unique_items = []
        for cl_item_proj in cl_items.keys():
            for item_type in cl_items[cl_item_proj]:
                for currency in cl_items[cl_item_proj][item_type]:
                    for item_price in cl_items[cl_item_proj][item_type][currency]:
                        netto_sum = 0
                        vat_sum = 0
                        start_date = 2147428700000
                        end_date = 0
                        units = 0.0
                        for cl_item in cl_items[cl_item_proj][item_type][currency][
                            item_price
                        ]:
                            units += cl_item.nth
                            netto = int(cl_item.nth * cl_item.unit_price)
                            netto_sum += netto
                            if cl_item.vat and cl_item.vat > 0:
                                vat = netto // 100 * cl_item.vat
                                vat_sum += vat
                            if cl_item.created < start_date:
                                start_date = cl_item.created
                            if cl_item.created > end_date:
                                end_date = cl_item.created
                        unique_items.append(
                            dict(
                                service=item_type,
                                description=f"Work for project {cl_item_proj}: {start_date} - {end_date}",
                                units=float(int(units * 100) / 100),
                                unit_price=item_price,
                                netto=netto_sum,
                                vat=vat_sum,
                                currency=currency,
                            )
                        )
        return unique_items

    def get_clients_with_lineitems(self):
        selected_clients = []
        selected_projects = []
        client_service = ClientService(fetcher=ClientDataFetcher())
        clients = client_service.get_clients_names()
        for client in clients:
            project_service = ProjectService(fetcher=ProjectDataFetcher(client))
            line_item_service = LineItemService(fetcher=LineItemDataFetcher(client))
            projects = project_service.get_projects_names()
            for project in projects:
                line_items = line_item_service.get_line_items(
                    client=client, project=project
                )
                if line_items:
                    selected_clients.append(client)
                    selected_projects.append(project)
        return [[*set(selected_clients)], [*set(selected_projects)]]

    def update_line_items(
        self, client: Client, line_items: [LineItem], invoiced: bool = True
    ):
        project_service = ProjectService(fetcher=ProjectDataFetcher(client))
        for line_item in line_items:
            project = project_service.get_project(line_item.project)
            line_item_service = LineItemService(
                fetcher=LineItemDataFetcher(client, project)
            )
            client_line_items_path = line_item_service.fetcher.get_line_items_path()

            filepath = f"{client_line_items_path}/{line_item.id}.yml"
            li = FileIO.read_yaml_file(filepath)
            li["invoiced"] = invoiced
            FileIO.save_yaml_file(filepath, li)

    def invoices_paid(self, invoices: [Invoice]):
        for invoice in invoices:
            invoice.paid_date = datetime.now().strftime("%Y-%m-%d")
            current_status = invoice.status
            invoice.status = InvoiceStatus.PAID
            # update line items on the actual invoice as well!
            for item in invoice.line_items:
                item.invoiced = True
                item.changed = datetime.now()
            self.save_invoice(invoice, current_status)
            if invoice.status != current_status:
                self.move_invoice(invoice, current_status)

    def invoices_sent(self, invoices: [Invoice]):
        for invoice in invoices:
            invoice.sent_date = datetime.now().strftime("%Y-%m-%d")
            current_status = invoice.status
            invoice.status = InvoiceStatus.SENT
            for item in invoice.line_items:
                item.invoiced = True
                item.changed = datetime.now()
            self.save_invoice(invoice, current_status)
            if invoice.status != current_status:
                self.move_invoice(invoice, current_status)

    def rollback(self, client: Client, invoice: Invoice):
        self.update_line_items(client, invoice.line_items, False)
        self.delete_invoice(invoice)

    def save_invoice(self, invoice: Invoice, current_status: InvoiceStatus):
        invoices_path = self.get_invoice_path_from_status(current_status)
        filepath = f"{invoices_path}/{invoice.id}.yml"
        FileIO.save_yaml_file(filepath, invoice.to_yaml())

    def move_invoice(self, invoice: Invoice, current_status: InvoiceStatus):
        invoices_path = self.get_invoice_path_from_status(current_status)
        filepath = f"{invoices_path}/{invoice.id}.yml"
        new_invoices_path = self.get_invoice_path_from_status(invoice.status)
        new_filepath = f"{new_invoices_path}/{invoice.id}.yml"
        FileManager.move_file(filepath, new_filepath)

    def delete_invoice(self, invoice):
        invoices_not_sent_path = self.fetcher.get_not_sent_invoices_path()
        filepath = f"{invoices_not_sent_path}/{invoice.id}.yml"
        FileIO.delete_yaml_file(filepath)

    def generate(self, client, invoice):
        me_service = MeService(fetcher=MeDataFetcher())
        me = me_service.get_me()
        generate(me, client, invoice)

    def get_invoice_name(self, projects: [str]):
        # get last invoice number form me.yml
        next_invoice_number = self.get_next_invoice_number()
        projects = "-".join([p for p in projects])
        return f"{next_invoice_number}-{date.today().strftime('%Y%m%d')}-{projects}"

    def get_next_invoice_number(self):
        me_service = MeService(fetcher=MeDataFetcher())
        me = me_service.get_me()
        if not me.last_invoice:
            return 1
        return me.last_invoice + 1

    def update_next_invoice_number(self, next_number):
        me_service = MeService(fetcher=MeDataFetcher())
        me = me_service.get_me()
        me.last_invoice = next_number
        me.write_to_file(me_service.fetcher.get_me_path())

    def get_selected_invoice(self, choices: list = []) -> Invoice | bool:
        invoices = self.get_invoices()
        selected = InvoiceInput.ask_select_invoice(choices)
        if str(selected) not in choices:
            return False
        return next(
            (invoice for invoice in invoices if invoice.number == selected), False
        )

    def get_selected_invoices(self, choices: [str] = None) -> [Invoice]:
        if choices is None:
            choices = []
        invoices = self.get_invoices()
        selecteds = InvoiceInput.ask_select_invoices(choices)
        selected_invoices = []
        for selected in selecteds:
            for invoice in invoices:
                if invoice.number == selected:
                    selected_invoices.append(invoice)
        if not selected_invoices:
            return False
        return selected_invoices

    def get_invoice_path_from_status(self, status: InvoiceStatus):
        if status == InvoiceStatus.CREATED.value:
            return self.fetcher.get_not_sent_invoices_path()
        if status == InvoiceStatus.SENT.value:
            return self.fetcher.get_sent_invoices_path()
        if status == InvoiceStatus.PAID.value:
            return self.fetcher.get_paid_invoices_path()
        if status == InvoiceStatus.CLOSED.value:
            return self.fetcher.get_pdf_invoices_path()

    def create_invoice(
        self,
        subject,
        client,
        projects,
        line_items,
        netto_sum,
        vat,
        currency,
        credit,
        discount,
        discount_percent,
        deposit,
        deposit_vat,
        deposit_text,
        our_ref,
        their_ref,
    ) -> None:
        invoices_not_sent_path = self.fetcher.get_not_sent_invoices_path()
        created = datetime.now()
        created_date = created.strftime("%Y-%m-%d")

        # defaults = Invoice.get_defaults()
        next_invoice_number = int(self.get_next_invoice_number())
        due_date = (date.today() + timedelta(days=credit)).strftime("%Y-%m-%d")
        total_sum = netto_sum + vat

        invoice_data = Invoice(
            id=self.get_invoice_name(projects=projects),
            number=next_invoice_number,
            subject=subject,
            client=client,
            projects=projects,
            line_items=line_items,
            netto_sum=netto_sum,
            vat=vat,
            total_sum=total_sum,
            currency=currency,
            credit=credit,
            discount=discount,
            discount_percent=discount_percent,
            deposit=deposit,
            deposit_vat=deposit_vat,
            deposit_text=deposit_text,
            created=created,
            created_date=created_date,
            due_date=due_date,
            sent_date=False,
            paid_date=False,
            reminder_date=False,
            status=InvoiceStatus.CREATED,
            our_ref=our_ref,
            their_ref=their_ref,
        )

        invoice_handle = self.fetcher.join_path(
            [invoices_not_sent_path, f"{self.get_invoice_name(projects=projects)}.yml"]
        )
        invoice_data.write_to_file(invoice_handle)
        self.update_line_items(client=self.fetcher.client, line_items=line_items)
        self.update_next_invoice_number(next_invoice_number)
