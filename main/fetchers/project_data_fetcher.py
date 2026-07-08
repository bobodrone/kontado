import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager, YamlFileManager
from main.models.client import Client
from main.models.project import Project


class ProjectDataFetcher(DataFetcher):
    client: Client

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def read_data(self):
        client_projects_path = self.get_projects_path()
        projects = []
        for project_folder in FolderManager.iterate(
            folder=client_projects_path, is_file=False
        ):
            project_file = f"{project_folder.name}.yml"
            project_path = FolderManager.join_path(
                [client_projects_path, project_folder, project_file]
            )
            project_yml = YamlFileManager.read(project_path)
            project = Project.from_yaml(project_yml)
            projects.append(project)
        return projects

    def get_projects_path(self):
        return f"{self.kontado_dir()}/clients/{self.client.name}/projects"
