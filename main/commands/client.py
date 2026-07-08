"""Handle client commands"""
import sys

from typing import Optional
import typer

from main.Exceptions.client import NoClientsFoundException, ClientFoundException
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.formatters.formatters import MessageFormatter
from main.formatters.client import (
    ClientListTableFormatter,
    ClientTableFormatter,
)
from main.inputs.client import ClientInput
from main.services.client import ClientService
from main.file_io import FileManager

app = typer.Typer()


@app.command(name="list")
def client_list():
    """Handle client list command"""

    service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    try:
        clients = service.get_clients()
        if not clients:
            raise NoClientsFoundException()
        client_list_formatter.print(clients)
    except Exception as e:
        MessageFormatter().error(e)


@app.command(name="show")
def client_show(client_name: Optional[str] = typer.Argument(None)):
    """Handle client show command"""
    try:
        service = ClientService(fetcher=ClientDataFetcher())
        if client_name:
            client = service.get_client(client_name)
            if not client:
                raise ClientFoundException(f"Could not find client: {client_name}")
            client_formatter = ClientTableFormatter(title=f"Client: {client.label}")
            client_formatter.print(client)
        else:
            clients = service.get_clients()
            if not clients:
                raise NoClientsFoundException()
            client_list_formatter = ClientListTableFormatter(title="Clients")
            client_list_formatter.print(clients)
            client = service.get_selected_client(
                choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
            )
            client_formatter = ClientTableFormatter(title=f"Client: {client.label}")
            client_formatter.print(client)
    except Exception as e:
        MessageFormatter().error(e)


@app.command(name="create")
def client_create():
    """Handle client create command"""
    service = ClientService(fetcher=ClientDataFetcher())
    client_name = ClientInput.ask_client_machine_name()

    if service.client_exists(client_name):
        MessageFormatter().error(f"Client folder: {client_name} already exists!")
        sys.exit()
    label = ClientInput.ask_client_full_name()
    if not label:
        MessageFormatter().error("No client name was given.")
        sys.exit()
    confirm = ClientInput.ask_confirm_create_client(client_name)
    if confirm:
        service.create_client(name=client_name, label=label)
        MessageFormatter().status(f"Client: {client_name} was created!")
    else:
        MessageFormatter().error("Aborting create client.")
        sys.exit()


if __name__ == "__main__":
    if not FileManager.get_kontado_dir():
        print("There is no kontado project found is this folder.")
        sys.exit()
    app()
