import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager, YamlFileManager
from main.models.client import Client
from main.models.project import Project
from main.models.invoice import Invoice, LineItem


class InvoiceDataFetcher(DataFetcher):
    client: Client

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def read_data(self):
        client_invoices_path = self.get_invoices_path()
        sub_folders = [
            self.get_paid_invoices_path(),
            self.get_sent_invoices_path(),
            self.get_not_sent_invoices_path(),
        ]
        invoices = []
        for invoice_file in FolderManager.iterate_sub_folders(
            main_folder=client_invoices_path, sub_folders=sub_folders, is_file=True
        ):
            invoice_path = FolderManager.join_path([client_invoices_path, invoice_file])
            invoice_yml = YamlFileManager.read(invoice_path)
            invoice = Invoice.from_yaml(invoice_yml)
            invoices.append(invoice)
        return invoices

    def get_invoices_path(self):
        return f"{self.kontado_dir()}/clients/{self.client.name}/invoices"

    def get_not_sent_invoices_path(self):
        return f"{self.get_invoices_path()}/not_sent"

    def get_paid_invoices_path(self):
        return f"{self.get_invoices_path()}/paid"

    def get_sent_invoices_path(self):
        return f"{self.get_invoices_path()}/sent"

    def get_pdf_invoices_path(self):
        return f"{self.get_invoices_path()}/pdf"
