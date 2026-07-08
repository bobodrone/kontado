""" Handle project commands"""
import sys

import typer

from main.Exceptions.client import NoClientsFoundException
from main.Exceptions.project import NoProjectsFoundException
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.invoice_data_fetcher import InvoiceDataFetcher
from main.fetchers.line_item_data_fetcher import LineItemDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.file_io import FileManager
from main.formatters.client import ClientListTableFormatter
from main.formatters.line_item import LineItemListTableFormatter
from main.inputs.project import ProjectInput
from main.formatters.project import (
    ProjectTableFormatter,
    ProjectListTableFormatter,
)
from main.formatters.formatters import MessageFormatter
from main.services.client import ClientService
from main.services.invoice import InvoiceService
from main.services.line_item import LineItemService
from main.services.project import ProjectService


app = typer.Typer()


@app.command(name="list")
def project_list() -> None:
    """Handle project list command"""

    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    try:
        clients = client_service.get_clients()
        if not clients:
            raise NoClientsFoundException()
        client_list_formatter.print(clients)

        selected_client = client_service.get_selected_client(
            choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
        )

        project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))

        projects = project_service.get_projects()
        if not projects:
            raise NoProjectsFoundException()
        project_list_formatter = ProjectListTableFormatter(title="Projects")
        project_list_formatter.print(projects)
    except Exception as e:
        MessageFormatter().error(e)


@app.command()
def show() -> None:
    """Handle project show command"""
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    try:
        clients = client_service.get_clients()
        if not clients:
            raise NoClientsFoundException()
        client_list_formatter.print(clients)

        selected_client = client_service.get_selected_client(
            choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
        )

        project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))

        projects = project_service.get_projects()
        if not projects:
            raise NoProjectsFoundException()
        project_list_formatter = ProjectListTableFormatter(title="Projects")
        project_list_formatter.print(projects)

        selected_project = project_service.get_selected_project(
            choices=[str(choice) for choice in range(1, len(projects) + 1, 1)]
        )

        project_formatter = ProjectTableFormatter(
            title=f"Project: {selected_project.label} for client: {selected_client.label}",
        )
        project_formatter.print(selected_project)
    except Exception as e:
        MessageFormatter().error(e)


@app.command()
def create() -> None:
    """Handle project create command"""
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    try:
        clients = client_service.get_clients()
        if not clients:
            raise NoClientsFoundException()
        client_list_formatter.print(clients)
    except Exception as e:
        MessageFormatter().error(e)

    selected_client = client_service.get_selected_client(
        choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
    )

    MessageFormatter().status(
        f"Let us create a new project for {selected_client.label}!"
    )

    project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))

    project_name = ProjectInput.ask_project_name()
    if project_service.project_exists(project_name):
        MessageFormatter().error(f"Project: {project_name} already exists!")
        sys.exit()
    # Gather input for a project
    project_label = ProjectInput.ask_project_full_name()
    description = ProjectInput.ask_project_description()
    confirm = ProjectInput.ask_confirm_create_project(
        selected_client.name, project_name, project_label
    )
    if confirm:
        project_service.create_project(
            client=selected_client.name,
            name=project_name,
            label=project_label,
            description=description,
        )
        project = project_service.get_project(project_name)
        project_formatter = ProjectTableFormatter(
            title=f"Project: {project.label} for client: {selected_client.label}",
        )
        project_formatter.print(project)
    else:
        MessageFormatter().error("Aborted creating a project!")
        sys.exit()


if __name__ == "__main__":
    if not FileManager.get_kontado_dir():
        print("There is no kontado project found is this folder.")
        sys.exit()
    app()
