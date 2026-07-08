from rich.prompt import Prompt, IntPrompt
from rich.prompt import Confirm


class ClientInput:
    """Class to handle the client object"""

    @staticmethod
    def ask_client_machine_name():
        return Prompt.ask("[green]Client folder name: [a-z]")

    @staticmethod
    def ask_client_full_name():
        return Prompt.ask("[green]Client full name: (label)")

    @staticmethod
    def ask_select_client(choices: list):
        return IntPrompt.ask(
            f"[green]Select client above, pick the number", choices=choices
        )

    @staticmethod
    def ask_confirm_create_client(client_name):
        return Confirm.ask(
            f"Are you sure you would like to create client: {client_name}"
        )
