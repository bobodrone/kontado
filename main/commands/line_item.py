import sys
from datetime import datetime

import typer
from csv import DictReader

from config import settings
from main.Exceptions.client import NoClientsFoundException
from main.Exceptions.project import (
    NoProjectsFoundException,
    NoProjectTasksFoundException,
)
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.line_item_data_fetcher import LineItemDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.file_io import FileManager
from main.formatters.client import ClientListTableFormatter
from main.formatters.formatters import MessageFormatter
from main.formatters.project import ProjectListTableFormatter, TasksListTableFormatter
from main.inputs.line_item import LineItemInput
from main.models.rate import Rate
from main.models.task import Task
from main.services.client import ClientService
from main.services.git_service import GitService
from main.services.line_item import LineItemService
from main.services.project import ProjectService

app = typer.Typer()


@app.command(name="create")
def line_item_create() -> None:
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
    project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))
    projects = project_service.get_projects()
    if not projects:
        raise NoProjectsFoundException()
    project_list_formatter = ProjectListTableFormatter(
        title=f"Projects for {selected_client.label}"
    )
    project_list_formatter.print(projects)

    selected_project = project_service.get_selected_project(
        choices=[str(choice) for choice in range(1, len(projects) + 1, 1)]
    )

    tasks = project_service.get_project_tasks(selected_project)
    tasks.append(
        Task(
            type="other",
            label="Other",
            default=False,
            rate=Rate(amount=0, currency="", type="", vat=0),
        ),
    )
    if not tasks:
        raise NoProjectTasksFoundException()
    project_task_list_formatter = TasksListTableFormatter(
        title=f"Tasks for: {selected_client.label} - {selected_project.label}"
    )
    project_task_list_formatter.print(tasks)

    selected_task = project_service.get_selected_project_task(
        selected_project,
        choices=[str(choice) for choice in range(1, len(tasks) + 1, 1)],
    )

    if selected_task.type != "other":
        line_item_type = "service"
        description = LineItemInput.ask_line_item_description()
        nth = LineItemInput.ask_line_item_nth_units()
        if not nth:
            nth = 1.0
        nth = float(nth)
        unit_price = selected_task.rate.amount
        task = selected_task.type
        vat = selected_task.rate.vat
        currency = selected_task.rate.currency
    else:
        task_names = [task.type for task in tasks]
        task_default = [task.type for task in tasks if task.default][0]
        vat_default = [task.rate.vat for task in tasks if task.default][0]
        print("Create a new line item")
        line_item_type = LineItemInput.ask_line_item_type()
        if not line_item_type:
            line_item_type = "service"
        description = LineItemInput.ask_line_item_description()
        nth = LineItemInput.ask_line_item_nth_units()
        if not nth:
            nth = 1.0
        nth = float(nth)
        unit_price = float(LineItemInput.ask_line_item_unit_price(
            settings.DEFAULT_RATE_AMOUNT,
            settings.DEFAULT_RATE_CURRENCY,
            settings.DEFAULT_RATE_TYPE,
        ))
        if not unit_price:
            unit_price = float(settings.DEFAULT_RATE_AMOUNT)
        currency = settings.DEFAULT_RATE_CURRENCY
        unit_price = unit_price
        task = LineItemInput.ask_line_item_tasks(task_names)
        if not task:
            task = task_default
        vat = LineItemInput.ask_line_item_vat()
        if not vat:
            vat = vat_default
        vat = vat

    line_item_service = LineItemService(
        fetcher=LineItemDataFetcher(selected_client, selected_project)
    )

    saved_file, saved_line_item = line_item_service.create_line_item(
        client=selected_client.name,
        project=selected_project.name,
        type=line_item_type,
        description=description,
        nth=nth,
        unit_price=unit_price,
        task=task,
        vat=vat,
        currency=currency,
    )
    git_commit = LineItemInput.confirm_git_commit()
    if git_commit:
        git_service = GitService()
        git_service.git_add(saved_file)
        git_service.git_commit(
            message=f"Added line item for {selected_client.name}/{selected_project.name} with {nth}h"
        )


@app.command(name="import")
def line_item_import(csv_file: str) -> None:
    client_service = ClientService(fetcher=ClientDataFetcher())
    with open(csv_file, "r") as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        clients = {}
        for item in list_of_dict:
            if item["client"] not in clients.keys():
                selected_client = client_service.get_client(item["client"])
                line_item_service = LineItemService(
                    fetcher=LineItemDataFetcher(selected_client)
                )
                clients[item["client"]] = {
                    "client": selected_client,
                    "service": line_item_service,
                }
            created_str = f"{item['Date']} {item['To']}"
            created_dt = datetime.strptime(created_str, "%Y-%m-%d %H:%M")
            saved_file, saved_line_item = clients[item["client"]][
                "service"
            ].create_line_item(
                client=item["client"],
                project=item["project"],
                type="service",
                description=item["description"],
                nth=float(item["nth"]),
                unit_price=int(item["unit_price"]) * 100,
                task=item["task"],
                vat=25,
                currency="SEK",
                created=created_dt,
            )


if __name__ == "__main__":
    if not FileManager.get_kontado_dir():
        print("There is no kontado project found is this folder.")
        sys.exit()
    app()
