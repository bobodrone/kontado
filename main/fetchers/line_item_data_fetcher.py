import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import YamlFileManager, FolderManager
from main.models.client import Client
from main.models.line_item import LineItem
from main.models.project import Project


class LineItemDataFetcher(DataFetcher):
    client: Client

    def __init__(self, client: Client, project: Project):
        super().__init__()
        self.client = client
        self.project = project

    def read_data(self):
        line_item_path = self.get_line_items_path()
        line_items = []
        for project_file in FolderManager.iterate(folder=line_item_path, is_file=True):
            line_item_path = FolderManager.join_path([line_item_path, project_file])
            line_item_yml = YamlFileManager.read(line_item_path)
            line_item = LineItem.from_yaml(line_item_yml)
            line_items.append(line_item)
        return line_items

    def get_line_items_path(self):
        return f"{self.kontado_dir()}/clients/{self.client.name}/projects/{self.project.name}/line_items"

    def get_next_num(self, created_at):
        line_item_path = self.get_line_items_path()
        largest_number = 0
        for line_item__file in FolderManager.iterate(
            folder=line_item_path, is_file=True
        ):
            if line_item__file.name.startswith(
                f"{self.client.name}-{self.project.name}-{created_at}-"
            ):
                start = len(f"{self.client.name}-{self.project.name}-{created_at}-")
                end = start + 4
                current_number = int(line_item__file.name[start:end])
                if current_number > largest_number:
                    largest_number = current_number
        largest_number += 1
        return format(largest_number, "04")
