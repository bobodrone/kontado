"""Main command line bootstrap file"""

import typer

from main.fetchers.timer_data_fetcher import TimerDataFetcher
from main.init.init import initialize
import main.commands.client
import main.commands.project
import main.commands.timer
import main.commands.line_item
import main.commands.invoice
from main.services.timer import TimerService
from rich import print

app = typer.Typer()


@app.command(name="init")
def init():
    """Initialize kontado"""
    initialize()


# app.add_typer(main.init.commands.app, name="init")
app.add_typer(
    main.commands.client.app,
    name="client",
    help="Client commands: list, show create",
)

app.add_typer(
    main.commands.project.app,
    name="project",
    help="Project commands: list, show create",
)

app.add_typer(
    main.commands.timer.app,
    name="timer",
    help="Timer commands: start, show, stop",
)

app.add_typer(
    main.commands.line_item.app,
    name="time",
    help="Time commands: create",
)

app.add_typer(
    main.commands.invoice.app,
    name="invoice",
    help="Invoice commands: list, paid",
)


def check_timer():
    timer_service = TimerService(fetcher=TimerDataFetcher())
    if timer_service.kontado_dir():
        if timer_service.time_check_running_timer():
            timer = timer_service.get_timer()
            duration = timer_service.time_calculate_time_difference(
                timer.start, timer_service.time_current_time()
            )
            print(f"\n\n[red]***** Timer is running for {duration} *****\n\n")


if __name__ == "__main__":
    app()
