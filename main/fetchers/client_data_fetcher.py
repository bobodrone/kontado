import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager, YamlFileManager
from main.models.client import Client


class ClientDataFetcher(DataFetcher):
    def read_data(self):
        clients_folder = self.get_clients_path()
        clients = []
        for folder in FolderManager.iterate(clients_folder):
            client_yml_path = f"{folder.path}/client.yml"
            client_yml = YamlFileManager.read(client_yml_path)
            client = Client.from_yaml(client_yml)
            clients.append(client)
        return clients

    def get_clients_path(self):
        return f"{self.kontado_dir()}/clients"
