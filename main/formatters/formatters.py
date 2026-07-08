from rich.console import Console
from rich.table import Table
from abc import ABC, abstractmethod
from rich import print


class Formatter(ABC):
    settings = {}

    def __init__(self, settings: dict = None):
        if settings:
            self.settings = settings

    def print(self, data: any) -> None:
        print(data)

    @staticmethod
    def append_to_list(list, value_to_check, append_value=None):
        if not value_to_check:
            return list
        else:
            list.append(append_value if append_value else value_to_check)
            return list


class MessageFormatter(Formatter):
    color: str = None

    def __init__(self):
        super().__init__()
        self.color = "green"

    def status(self, data: any):
        print(f"[{self.color}]{data}")

    def warning(self, data: any):
        self.color = "yellow"
        print(f"[{self.color}]{data}")

    def error(self, data: any):
        self.color = "red"
        print(f"[{self.color}]{data}")


class TableFormatter(Formatter):
    table = None

    def __init__(
        self,
        title: str,
        settings: dict = None,
    ):
        super().__init__(settings)
        self.create_table(title)

    def create_table(self, title, show_lines=False):
        self.table = Table(title=title, show_lines=show_lines)

    def format_table(self, data: any):
        pass

    def print(self, data) -> None:
        self.format_table(data)
        console = Console()
        console.print(self.table)
