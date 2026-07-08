import sys
from datetime import datetime

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager, FileManager
from main.formatters.formatters import MessageFormatter
from main.inputs.client import ClientInput
from main.models.address import Address
from main.models.client import Client
from main.models.company_info import CompanyInfo
from main.models.contact import Contact
from main.services.service import Service


class ClientService(Service):
    clients: [Client]

    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher
        self.clients = None

    def get_clients(self, no_cache=False) -> [Client]:
        if self.clients and not no_cache:
            return self.clients
        clients = self.fetcher.read_data()
        if clients:
            self.clients = clients
        return clients

    def get_client(self, name) -> Client | None:
        clients = [c for c in self.get_clients(no_cache=True) if c.name == name]
        if not clients:
            return None
        return clients.pop()

    def get_selected_client(self, choices: list = []) -> Client | None:
        selected = ClientInput.ask_select_client(choices)
        if selected not in range(1, len(self.clients) + 1):
            return None
        return self.clients[selected - 1]

    def get_clients_names(self) -> [str]:
        clients = []
        client_objects = self.get_clients()
        for client_object in client_objects:
            clients.append(client_object.name)
        return clients

    def client_exists(self, name) -> bool:
        return name in self.get_clients_names()

    def create_client_folders(self, client_name: str):
        clients_path = self.fetcher.get_clients_path()
        path = self.fetcher.join_path([clients_path, client_name])
        projects_path = self.fetcher.join_path([clients_path, client_name, "projects"])
        invoices_path = self.fetcher.join_path([clients_path, client_name, "invoices"])
        invoices_sent_path = self.fetcher.join_path([invoices_path, "sent"])
        invoices_payed_path = self.fetcher.join_path([invoices_path, "paid"])
        invoices_not_sent_path = self.fetcher.join_path([invoices_path, "not_sent"])
        invoices_pdf_path = self.fetcher.join_path([invoices_path, "pdf"])

        dirs_to_create = [
            path,
            projects_path,
            invoices_path,
            invoices_sent_path,
            invoices_payed_path,
            invoices_not_sent_path,
            invoices_pdf_path,
        ]
        for directory in dirs_to_create:
            if not FolderManager.folder_exist(directory):
                FolderManager.create_folder(directory)
                FileManager.create(self.fetcher.join_path([directory, ".gitkeep"]), "")

    def create_client(self, name: str, label: str) -> None:
        clients_path = self.fetcher.get_clients_path()
        # Create all config yml files in the config folder
        curr_dt = datetime.now()
        created = int(round(curr_dt.timestamp()))
        defaults = Client.get_defaults()
        client_data = Client(
            name=name,
            label=label,
            language=defaults["language"],
            description=defaults["description"],
            company_info=CompanyInfo(
                name=defaults["company_info"]["name"],
                orgnr=defaults["company_info"]["orgnr"],
                vatnr=defaults["company_info"]["vatnr"],
                postal_address=Address(
                    co=defaults["company_info"]["postal_address"]["co"],
                    thoroughfare=defaults["company_info"]["postal_address"][
                        "thoroughfare"
                    ],
                    premise=defaults["company_info"]["postal_address"]["premise"],
                    postalcode=defaults["company_info"]["postal_address"]["postalcode"],
                    locality=defaults["company_info"]["postal_address"]["locality"],
                    region=defaults["company_info"]["postal_address"]["region"],
                    country=defaults["company_info"]["postal_address"]["country"],
                ),
                visitor_address=Address(
                    co=defaults["company_info"]["visitor_address"]["co"],
                    thoroughfare=defaults["company_info"]["visitor_address"][
                        "thoroughfare"
                    ],
                    premise=defaults["company_info"]["visitor_address"]["premise"],
                    postalcode=defaults["company_info"]["visitor_address"][
                        "postalcode"
                    ],
                    locality=defaults["company_info"]["visitor_address"]["locality"],
                    region=defaults["company_info"]["visitor_address"]["region"],
                    country=defaults["company_info"]["visitor_address"]["country"],
                ),
            ),
            contacts=[
                Contact(
                    person=defaults["contacts"][0]["person"],
                    title=defaults["contacts"][0]["title"],
                    email=defaults["contacts"][0]["email"],
                    phone=defaults["contacts"][0]["phone"],
                )
            ],
            invoice_emails=[],
            last_invoice=0,
            currency=defaults["currency"],
            created=created,
            changed=created,
        )

        self.create_client_folders(name)
        client_handle = self.fetcher.join_path([clients_path, name, "client.yml"])
        client_data.write_to_file(client_handle)
