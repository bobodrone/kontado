import sys

from typing import Optional
import typer
from typing_extensions import Annotated
from config import settings
from main.Exceptions.client import NoClientsFoundException
from main.Exceptions.project import (
    NoProjectsFoundException,
    NoProjectTasksFoundException,
)
from main.fetchers.client_data_fetcher import ClientDataFetcher
from main.fetchers.invoice_data_fetcher import InvoiceDataFetcher
from main.fetchers.line_item_data_fetcher import LineItemDataFetcher
from main.fetchers.project_data_fetcher import ProjectDataFetcher
from main.file_io import FileManager
from main.formatters.client import ClientListTableFormatter
from main.formatters.formatters import MessageFormatter
from main.formatters.invoice import InvoiceListTableFormatter
from main.formatters.line_item import (
    LineItemListTableFormatter,
    LineItemListGroupedTableFormatter,
)
from main.formatters.project import ProjectListTableFormatter, TasksListTableFormatter
from main.inputs.invoice import InvoiceInput
from main.inputs.line_item import LineItemInput
from main.models.invoice import InvoiceStatus
from main.models.rate import Rate
from main.models.task import Task
from main.services.client import ClientService
from main.services.invoice import InvoiceService
from main.services.line_item import LineItemService
from main.services.project import ProjectService

app = typer.Typer()


@app.command(name="list")
def invoice_list(
    status: Annotated[str, typer.Option(help="created, sent, paid status")] = "",
) -> None:
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
        invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))
        if not status:
            invoices = invoice_service.get_invoices()
        else:
            invoices = invoice_service.get_invoices(InvoiceStatus(status))
        if not invoices:
            print("error no invoices")
            # raise NoInvoicesFoundException()
        invoices_formatter = InvoiceListTableFormatter(
            title=f"Invoices for: {selected_client.name}"
        )
        invoices_formatter.print(invoices)
    except Exception as e:
        MessageFormatter().error(e)


@app.command(name="uninvoiced")
def invoice_uninvoiced() -> None:
    """Handle project uninvoiced command"""
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

        invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))
        project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))

        projects = project_service.get_projects()
        if not projects:
            raise NoProjectsFoundException()
        project_list_formatter = ProjectListTableFormatter(title="Projects")
        project_list_formatter.print(projects)

        # select multiple projects
        selected_projects = project_service.get_selected_projects(
            choices=[str(choice) for choice in range(1, len(projects) + 1, 1)]
        )
        collected_line_items = invoice_service.collect_grouped_line_items(
            client=selected_client, projects=selected_projects
        )

        if not collected_line_items:
            project_names = [p.name for p in selected_projects]
            MessageFormatter().error(
                f"\nThere were no un-invoiced line items found for the client: {selected_client.name} and project(s): {', '.join(project_names)}..."
            )
            sys.exit()

        netto_sum = 0
        vat_sum = 0

        for item_project in collected_line_items.keys():
            for service in collected_line_items[item_project]:
                for currency in collected_line_items[item_project][service]:
                    for item_price in collected_line_items[item_project][service][
                        currency
                    ]:
                        for collected_line_item in collected_line_items[item_project][
                            service
                        ][currency][item_price]:
                            netto = int(
                                collected_line_item.nth * collected_line_item.unit_price
                            )
                            vat = netto // 100 * collected_line_item.vat
                            netto_sum += netto
                            vat_sum += vat

        settings = {
            "sums": {
                "netto_sum": netto_sum,
                "vat": vat_sum,
            }
        }

        line_formatter = LineItemListGroupedTableFormatter(
            title=f"Uninvoices items for: {selected_client.name}", settings=settings
        )

        line_formatter.print(collected_line_items)
    except Exception as e:
        MessageFormatter().error(e)


@app.command(name="rollback")
def invoice_rollback() -> None:
    # Fetch list of client models
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    clients = client_service.get_clients()
    if not clients:
        raise NoClientsFoundException()
    client_list_formatter.print(clients)
    selected_client = client_service.get_selected_client(
        choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
    )
    # Fetch list of selected client's project models
    invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))
    invoice_list_formatter = InvoiceListTableFormatter(title="Invoices")
    invoices = invoice_service.get_invoices()
    if not invoices:
        print("no invoices")

    invoice_list_formatter.print(invoices)
    selected_invoice = invoice_service.get_selected_invoice(
        choices=[str(choice) for choice in range(1, len(invoices) + 1, 1)]
    )
    invoice_service.rollback(selected_client, selected_invoice)


@app.command(name="create")
def invoice_create(summarize: Optional[str] = typer.Argument(None)) -> None:
    freeform = InvoiceInput.ask_invoice_freeform()
    # Fetch list of client models
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    clients = client_service.get_clients()
    if not clients:
        raise NoClientsFoundException()
    client_list_formatter.print(clients)
    selected_client = client_service.get_selected_client(
        choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
    )

    # Fetch list of selected client's project models
    invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))
    project_service = ProjectService(fetcher=ProjectDataFetcher(selected_client))
    projects = project_service.get_projects()
    project_formatter = ProjectListTableFormatter(title="Projects")
    project_formatter.print(projects)

    if freeform:
        cl_items = []
        selected_project = project_service.get_selected_project(
            choices=[str(choice) for choice in range(1, len(projects) + 1, 1)]
        )
        # Collect line items
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

        no_more_line_items = False
        while not no_more_line_items:
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
                unit_price = LineItemInput.ask_line_item_unit_price(
                    settings.DEFAULT_RATE_AMOUNT,
                    settings.DEFAULT_RATE_CURRENCY,
                    settings.DEFAULT_RATE_TYPE,
                )
                if not unit_price:
                    unit_price = settings.DEFAULT_RATE_AMOUNT
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
                currency="SEK",  # change to project specific
            )
            cl_items.append(saved_line_item)
            no_more_line_items = InvoiceInput.ask_invoice_freeform_more_line_items()

    else:
        # Select multiple projects
        selected_projects = project_service.get_selected_projects(
            choices=[str(choice) for choice in range(1, len(projects) + 1, 1)]
        )

        cl_items = invoice_service.collect_line_items(
            client=selected_client, projects=selected_projects
        )

    if not cl_items:
        project_names = [p.name for p in selected_projects]
        MessageFormatter().error(
            f"\nThere were no un-invoiced line items found for the client: {selected_client.name} and project(s): {', '.join(project_names)}..."
        )
        sys.exit()

    line_formatter = LineItemListTableFormatter(
        title=f"Create an invoice for {selected_client.name} with the following items"
    )

    line_formatter.print(cl_items)
    line_item_confirm = InvoiceInput.ask_line_items_confirm()
    if not line_item_confirm:
        sys.exit()

    netto_sum = 0
    vat_sum = 0
    discount_amount = 0
    currency = "SEK"
    for item in cl_items:
        if item.currency != "SEK":
            currency = item.currency
        netto_sum = netto_sum + item.netto
        vat = 0
        if item.vat:
            vat = item.nth * item.unit_price * (item.vat / 100)
        vat_sum = vat_sum + vat

    discount = InvoiceInput.ask_invoice_discount()

    if discount and discount != 0:
        discount = float(discount)
        netto_sum = round(netto_sum)
        vat_sum = round(vat_sum)

        MessageFormatter().status(
            f"Total before discount: {netto_sum} (vat: {vat_sum})"
        )

        discount_amount = round((netto_sum * (discount / 100.0)))
        netto_sum = netto_sum - (netto_sum * (discount / 100.0))
        vat_sum = vat_sum - (vat_sum * (discount / 100.0))

        MessageFormatter().status(
            f"Total after discount ({discount_amount}): {round(netto_sum)} (vat: {round(vat_sum)})"
        )

    deposit = InvoiceInput.ask_invoice_deposit_amount()
    deposit_vat = 0
    deposit_text = ""
    if deposit:
        deposit_vat = InvoiceInput.ask_invoice_deposit_vat()
        deposit_text = InvoiceInput.ask_invoice_deposit_text()
        if deposit > 0:
            netto_sum -= deposit
            netto_sum -= deposit_vat

    netto_sum = round(netto_sum)
    vat_sum = round(vat_sum)
    MessageFormatter().status(f"Total amount: {netto_sum} (vat: {vat_sum})")

    confirm = InvoiceInput.ask_invoice_confirm()
    credit_days = 30
    if confirm:
        subject = InvoiceInput.ask_invoice_subject()
        credit = InvoiceInput.ask_invoice_credit(credit_days)
        if not credit:
            credit = credit_days

        their_ref = ""
        if selected_client.contacts:
            their_ref = selected_client.contacts[0].person or ""

        if their_ref == "":
            their_ref = InvoiceInput.ask_invoice_another_their_ref()
        else:
            confirm_their_ref = InvoiceInput.ask_invoice_confirm_their_ref(their_ref)
            if not confirm_their_ref:
                their_ref = InvoiceInput.ask_invoice_another_their_ref()

        invoice_service.create_invoice(
            subject=subject,
            client=selected_client.name,
            projects=[project.name for project in selected_projects],
            line_items=cl_items,
            netto_sum=netto_sum,
            vat=vat_sum,
            currency=currency,
            credit=credit,
            discount=discount_amount,
            discount_percent=discount,
            deposit=deposit,
            deposit_vat=deposit_vat,
            deposit_text=deposit_text,
            our_ref="Fredric Bergström",
            their_ref=their_ref,
        )
        # InvoiceService.update_line_items(selected_client.name, collected_line_items)


@app.command(name="pdf")
def invoice_pdf() -> None:
    client_service = ClientService(fetcher=ClientDataFetcher())
    client_list_formatter = ClientListTableFormatter(title="Clients")
    clients = client_service.get_clients()
    if not clients:
        raise NoClientsFoundException()

    client_list_formatter.print(clients)
    selected_client = client_service.get_selected_client(
        choices=[str(choice) for choice in range(1, len(clients) + 1, 1)]
    )

    invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))
    invoice_list_formatter = InvoiceListTableFormatter(title="Invoices")
    invoices = invoice_service.get_invoices()
    if not invoices:
        print("no invoices")
        # raise NoInvoicesFoundException()

    invoice_list_formatter.print(invoices)
    invoice_choices = [str(choice.number) for choice in invoices]
    selected_invoice = invoice_service.get_selected_invoice(
        # choices=[str(choice) for choice in range(1, len(invoices) + 1, 1)]
        choices=invoice_choices
    )

    invoice_service.generate(selected_client, selected_invoice)


@app.command(name="paid")
def invoice_paid() -> None:
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

        invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))

        invoices = invoice_service.get_invoices(InvoiceStatus.SENT)
        if not invoices:
            print("error no invoices")
            # raise NoInvoicesFoundException()
        invoices_formatter = InvoiceListTableFormatter(
            title=f"Invoices for: {selected_client.name}"
        )
        invoices_formatter.print(invoices)
        invoice_choices = [str(choice.number) for choice in invoices]
        selected_invoices = invoice_service.get_selected_invoices(
            choices=invoice_choices
        )
        invoice_service.invoices_paid(selected_invoices)

    except Exception as e:
        MessageFormatter().error(e)


@app.command(name="sent")
def invoice_sent() -> None:
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

        invoice_service = InvoiceService(fetcher=InvoiceDataFetcher(selected_client))

        invoices = invoice_service.get_invoices(InvoiceStatus.CREATED)
        if not invoices:
            print("error no invoices")
            # raise NoInvoicesFoundException()
        invoices_formatter = InvoiceListTableFormatter(
            title=f"Invoices for: {selected_client.name}"
        )
        invoices_formatter.print(invoices)
        invoice_choices = [str(choice.number) for choice in invoices]
        selected_invoices = invoice_service.get_selected_invoices(
            choices=invoice_choices
        )
        invoice_service.invoices_sent(selected_invoices)

    except Exception as e:
        MessageFormatter().error(e)


if __name__ == "__main__":
    if not FileManager.get_kontado_dir():
        print("There is no kontado project found is this folder.")
        sys.exit()
    app()
