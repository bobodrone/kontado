from datetime import datetime

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FileManager, FolderManager
from main.inputs.project import ProjectInput
from main.services.service import Service
from main.models.project import Project, Task


class ProjectService(Service):
    projects: [Project]

    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher
        self.projects = None

    def get_projects(self, no_cache=False, in_projects=None) -> [Project]:
        if self.projects and not no_cache:
            return self.projects
        projects = self.fetcher.read_data()
        if in_projects:
            return [project for project in projects if project.name in in_projects]
        if projects:
            self.projects = projects
        return projects

    def project_exists(self, project_name) -> bool:
        return project_name in self.get_projects_names()

    def get_projects_names(self) -> [str]:
        projects = []
        project_objects = self.get_projects()
        for project_object in project_objects:
            projects.append(project_object.name)
        return projects

    def get_project(self, project_name) -> Project | None:
        projects = [
            p for p in self.get_projects(no_cache=True) if p.name == project_name
        ]
        if not projects:
            return False
        return projects.pop()

    def create_project(
        self, client: str, name: str, label: str, description: str
    ) -> None:
        projects_path = self.fetcher.get_projects_path()
        curr_dt = datetime.now()
        created = int(round(curr_dt.timestamp()))
        defaults = Project.get_defaults(client)
        project_data = Project(
            client=client,
            name=name,
            label=label,
            description=defaults["description"],
            tasks=defaults["tasks"],
            created=created,
            changed=created,
        )

        projects_folder_path = self.fetcher.join_path([projects_path, name])
        line_items_folder_path = self.fetcher.join_path(
            [projects_folder_path, "line_items"]
        )
        dirs_to_create = [projects_folder_path, line_items_folder_path]
        for directory in dirs_to_create:
            if not FolderManager.folder_exist(directory):
                FolderManager.create_folder(directory)
                FileManager.create(self.fetcher.join_path([directory, ".gitkeep"]), "")
        project_handle = self.fetcher.join_path([projects_folder_path, f"{name}.yml"])
        project_data.write_to_file(project_handle)

    def get_selected_project(self, choices: list = []) -> Project:
        selected = ProjectInput.ask_select_project(choices)
        if selected not in range(1, len(self.projects) + 1):
            return False
        return self.projects[selected - 1]

    def get_selected_projects(self, choices=None) -> [Project]:
        if choices is None:
            choices = []
        selecteds = ProjectInput.ask_select_projects(choices)
        projects = []
        for selected in selecteds:
            if selected not in range(1, len(self.projects) + 1):
                return False
            projects.append(self.projects[selected - 1])
        return projects

    def get_selected_project_task(self, project, choices: list = []) -> Task:
        selected = ProjectInput.ask_select_project_task(choices)
        if selected not in range(1, len(project.tasks) + 1):
            return False
        return project.tasks[selected - 1]

    def get_project_tasks(self, project) -> [Task]:
        return project.tasks

    # def get_client(self, name) -> Client | None:
    #     clients = [c for c in self.get_clients() if c.name == name]
    #     if not clients:
    #         return False
    #     return clients.pop()
    #
    # def get_selected_client(self, choices: list = []) -> Client:
    #     selected = ClientInput.ask_select_client(choices)
    #     if selected not in range(1, len(self.clients) + 1):
    #         return False
    #     return self.clients[selected - 1]
    #
    # def get_clients_names(self) -> [str]:
    #     clients = []
    #     client_objects = self.get_clients()
    #     for client_object in client_objects:
    #         clients.append(client_object.name)
    #     return clients
    #
    # def client_exists(self, name) -> bool:
    #     return name in self.get_clients_names()
    #
    # def get_clients_path(self):
    #     return f"{self.fetcher.current_path()}/clients"


# def get_projects_path(client):
#     current_path = os.getcwd()
#     return f"{current_path}/clients/{client}/projects"
#
#
# def get_projects(client) -> [Project]:
#     projects = []
#     current_path = os.getcwd()
#     client_projects_path = f"{current_path}/clients/{client}/projects"
#
#     for project_file in FolderManager.iterate(
#         folder=client_projects_path, is_file=True
#     ):
#         project_path = FolderManager.join_path([client_projects_path, project_file])
#         project_yml = YamlFileManager.read(project_path)
#         project = Project.from_yaml(project_yml)
#         projects.append(project)
#     return projects
#
#
# def project_exists(client_name, project_name) -> bool:
#     projects = get_projects_names(client_name)
#     return project_name in projects
#
#
# def get_projects_names(client_name) -> [str]:
#     projects = []
#     project_objects = get_projects(client_name)
#     for project_object in project_objects:
#         projects.append(project_object.name)
#     return projects
#
#
# def get_project(client_name, project_name) -> Project:
#     projs = get_projects(client_name)
#     projects = [p for p in projs if p.name == project_name]
#     return projects.pop()
#
#
# def create_project(client, name, label, description) -> None:
#     projects_path = get_projects_path(client)
#     curr_dt = datetime.now()
#     created = int(round(curr_dt.timestamp()))
#     defaults = Project.get_defaults(client)
#     project_data = Project(
#         client=client,
#         name=name,
#         label=label,
#         description=defaults["description"],
#         tasks=defaults["tasks"],
#         created=created,
#         changed=created,
#     )
#     project_handle = FolderManager.join_path([projects_path, f"{name}.yml"])
#     project_data.write_to_file(project_handle)
#
#
# def get_selected_project(client_name) -> Project:
#     projects = get_projects(client_name)
#     index = 0
#     if not projects:
#         print(f"There are no projects created for client: {client_name}")
#     selected_project_index = ProjectInput.ask_select_project()
#     return projects[int(selected_project_index) - 1]
#
#
# def get_selected_project_task(project):
#     tasks = get_project_tasks(project)
#     index = 0
#     if not tasks:
#         print(f"There are no project tasks created for project: {project.name}")
#     selected_task_index = ProjectInput.ask_select_task()
#     return tasks[int(selected_task_index) - 1]
#
#
# def get_project_tasks(project):
#     return project.tasks
#
#
# class ProjectProcessor(BaseProcessor):
#     """Class to handle the project object"""
#
#     def get_projects(self, client) -> [Project]:
#         projects = []
#         client_projects_path = f"{self.settings.CLIENTS_FOLDER}/{client}/projects"
#         for project_file in FolderManager.iterate(
#             folder=client_projects_path, is_file=True
#         ):
#             project_path = FolderManager.join_path([client_projects_path, project_file])
#             project_yml = YamlFileManager.read(project_path)
#             project = Project.from_yaml(project_yml)
#             projects.append(project)
#         return projects
#
#     def get_projects_names(self, client_name) -> [str]:
#         projects = []
#         project_objects = self.get_projects(client_name)
#         for project_object in project_objects:
#             projects.append(project_object.name)
#         return projects
#
#     def get_project(self, client_name, project_name) -> Project:
#         projects = [p for p in self.get_projects(client_name) if p.name == project_name]
#         return projects.pop()
#
#     @staticmethod
#     def get_project_tasks(project):
#         return project.tasks
#
#     @staticmethod
#     def get_selected_project_task(project):
#         tasks = ProjectProcessor.get_project_tasks(project)
#         index = 0
#         if not tasks:
#             print(f"There are no project tasks created for project: {project.name}")
#         for task in tasks:
#             index = index + 1
#             print(
#                 f"{index}) {task.label} ({task.rate.amount} {task.rate.currency} / {task.rate.type})"
#             )
#         selected_task_index = ProjectInput.ask_select_task()
#         return tasks[int(selected_task_index) - 1]
#
#     @staticmethod
#     def list_projects(client) -> None:
#         projects = ProjectProcessor.get_projects(client)
#         index = 0
#         if not projects:
#             print(f"There are no projects created for client: {client}")
#         for project in projects:
#             index = index + 1
#             print(f"{index}) {project.label} ({project.name})")
#
#     @staticmethod
#     def get_selected_project(client_name) -> Project:
#         projects = ProjectProcessor.get_projects(client_name)
#         index = 0
#         if not projects:
#             print(f"There are no projects created for client: {client_name}")
#         for project in projects:
#             index = index + 1
#             print(f"{index}) {project.label} ({project.name})")
#         selected_project_index = ProjectInput.ask_select_project()
#         return projects[int(selected_project_index) - 1]
#
#     @staticmethod
#     def get_selected_projects(client_name) -> [dict]:
#         projects = ProjectProcessor.get_projects(client_name)
#         index = 0
#         if not projects:
#             print(f"There are no projects created for client: {client_name}")
#             exit()
#         for project in projects:
#             index = index + 1
#             print(f"{index}) {project['label']} ({project['name']})")
#         selected_project_indices = input(
#             "Select project(s) above, pick the number, separated with comma. "
#         )
#         selected_project_indices = selected_project_indices.split(",")
#         selected_projects = []
#         for selected_project_index in selected_project_indices:
#             if int(selected_project_index) - 1 in projects:
#                 selected_projects.append(projects[int(selected_project_index) - 1])
#             if not selected_projects:
#                 print(f"No valid project were selected! Try again...")
#                 exit()
#         return selected_projects
#
#     def exists(self, client_name, project_name) -> bool:
#         projects = self.get_projects_names(client_name)
#         return project_name in projects
#
#     @staticmethod
#     def check_project_exists(client, project) -> bool:
#         projects = ProjectProcessor.get_projects_names(client)
#         return project in projects
#
#     def create_project(self, client, name, label, description) -> None:
#         project = Project(
#             client=client, name=name, label=label, description=description
#         )
#         self.save_yaml(project)
#
#     def save_yaml(self, project) -> None:
#         clients_path = self.get_setting("CLIENTS_FOLDER")
#         defaults_path = self.get_setting("DEFAULTS_FOLDER")
#
#         if not FolderManager.folder_exist(clients_path):
#             FolderManager.create_folder(clients_path)
#
#         if project.client:
#             client_path = FolderManager.join_path([clients_path, project.client])
#
#             if not FolderManager.folder_exist(client_path):
#                 FolderManager.create_folder(client_path)
#
#             projects_path = FolderManager.join_path(
#                 [clients_path, project.client, "projects"]
#             )
#             if not FolderManager.folder_exist(projects_path):
#                 FolderManager.create_folder(projects_path)
#
#             default_path = FolderManager.join_path([defaults_path, "project.yml"])
#             filepath = FolderManager.join_path([projects_path, f"{project.name}.yml"])
#
#             yaml_dict = project.to_yaml()
#             defaults = YamlFileManager.read(default_path)
#
#             defaults["project"].update({"client": yaml_dict["client"]})
#             defaults["project"].update({"name": yaml_dict["name"]})
#             defaults["project"].update({"label": yaml_dict["label"]})
#             defaults["project"].update({"description": yaml_dict["description"]})
#             for task in defaults["project"]["tasks"]:
#                 if task["rate"]["type"] != "free":
#                     task.update(
#                         {
#                             "rate": {
#                                 "amount": self.get_setting("DEFAULT_RATE_AMOUNT"),
#                                 "currency": self.get_setting("DEFAULT_RATE_CURRENCY"),
#                                 "type": self.get_setting("DEFAULT_RATE_TYPE"),
#                                 "vat": self.get_setting("DEFAULT_RATE_VAT"),
#                             }
#                         }
#                     )
#             YamlFileManager.write(filepath, defaults)
#
#
# def get_default_tasks(self):
#     task_objects = []
#     for task in self.settings.DEFAULT_TASKS:
#         task_object = Task(
#             type=task["type"],
#             label=task["label"],
#             rate=task["rate"],
#             default=task["default"],
#         )
#         task_objects.append(task_object)
#     return task_objects
