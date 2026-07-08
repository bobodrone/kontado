import sys

import typer

from main.Exceptions.client import NoClientsFoundException
from main.Exceptions.project import (
    NoProjectsFoundException,
    NoProjectTasksFoundException,
)
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.line_item_data_fetcher import LineItemDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.fetchers.timer_data_fetcher import TimerDataFetcher
from main.file_io import FileManager
from main.formatters.client import ClientListTableFormatter
from main.formatters.formatters import MessageFormatter
from main.inputs.line_item import LineItemInput
from main.formatters.project import (
    ProjectListTableFormatter,
    TasksListTableFormatter,
)
from main.services.client import ClientService
from main.services.git_service import GitService
from main.services.line_item import LineItemService
from main.services.project import ProjectService
from main.services.timer import TimerService


app = typer.Typer()


@app.command(name="start")
def timer_start() -> None:
    timer_service = TimerService(fetcher=TimerDataFetcher())

    if timer_service.time_check_running_timer():
        timer = timer_service.get_timer()
        MessageFormatter().warning(
            f"Timer is already running for {timer.client}/{timer.project}/{timer.task} since {timer_service.time_ts2date(timer.start)}"
        )
        sys.exit()

    #    try:
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
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

    tasks = project_service.get_project_tasks(selected_project)
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

    timer_service.time_start_timer(
        client=selected_client.name,
        project=selected_project.name,
        task=selected_task,
    )
    print(
        f"Timer started {timer_service.time_ts2date(timer_service.time_current_time()).strftime('%Y-%m-%d %H:%M:%S')} for {selected_client.name}/{selected_project.name}"
    )
    #    except Exception as e:
    # MessageFormatter().error(e)


@app.command(name="status")
def timer_status() -> None:
    timer_service = TimerService(fetcher=TimerDataFetcher())
    if timer_service.time_check_running_timer():
        timer = timer_service.get_timer()
        duration = timer_service.time_calculate_time_difference(
            timer.start, timer_service.time_current_time()
        )
        print(f"Timer is running for {duration}")
        print(
            f"Since {timer_service.time_ts2date(timer.start).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print(f"Client: {timer.client}")
        print(f"Project: {timer.project}")
        print(f"Task: {timer.task}\n")
    else:
        print("Timer is not running.")


@app.command(name="stop")
def timer_stop() -> None:
    timer_service = TimerService(fetcher=TimerDataFetcher())
    timer_service.time_stop_timer()
    timer = timer_service.get_timer()
    duration = timer_service.time_calculate_time_difference(
        start=timer.start, stop=timer.end
    )
    hours = timer_service.time_round_up_to_closest((timer.end - timer.start) / 3600)
    MessageFormatter().status(
        f"Timer stopped {timer_service.time_ts2date(timer.end).strftime('%Y-%m-%d %H:%M:%S')} for: {timer.client}/{timer.project} with {duration} - {hours}h"
    )

    confirm_timer_duration = LineItemInput.confirm_timer_result_time()
    if not confirm_timer_duration:
        hours = LineItemInput.ask_timer_result_time()
    client_service = ClientService(fetcher=ClientDataFetcher())
    client = client_service.get_client(timer.client)
    project_service = ProjectService(fetcher=ProjectDataFetcher(client))
    project = project_service.get_project(timer.project)

    description = LineItemInput.ask_line_item_description()
    amount = 0
    vat = 0
    for task in project.tasks:
        if task.type == timer.task:
            amount = task.rate.amount
            vat = task.rate.vat

    line_item_service = LineItemService(fetcher=LineItemDataFetcher(client, project))
    saved_file, saved_line_item = line_item_service.create_line_item(
        client=timer.client,
        project=timer.project,
        type="service",
        description=description,
        nth=hours,
        unit_price=amount,
        task=timer.task,
        vat=vat,
        currency="SEK",  # change to project specific
    )
    git_commit = LineItemInput.confirm_git_commit()
    if git_commit:
        git_service = GitService()
        git_service.git_add(saved_file)
        git_service.git_commit(
            message=f"Added line item for {timer.client}/{timer.project} with {duration} - {hours}h"
        )


if __name__ == "__main__":
    if not FileManager.get_kontado_dir():
        print("There is no kontado project found is this folder.")
        sys.exit()
    app()
