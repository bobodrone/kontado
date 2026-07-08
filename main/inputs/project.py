from rich.prompt import Prompt, IntPrompt
from rich.prompt import Confirm
import re


class KPrompt(Prompt):
    def check_choice(self, value: str) -> bool:
        """Check value is in the list of valid choices.

        Args:
            value (str): Value entered by user.

        Returns:
            bool: True if choice was valid, otherwise False.
        """
        assert self.choices is not None
        clean = True
        selected = re.split(r",\s?", value.strip())
        for v in selected:
            if v.strip() not in self.choices:
                clean = False
        return clean


class ProjectInput:
    """Class to handle the project object"""

    @staticmethod
    def ask_project_name():
        while True:
            value = Prompt.ask("[green]Project folder name: [a-z, 0-9 and -] ")
            if re.fullmatch(r"[a-z0-9\-]+", value):
                break
            print("[prompt.invalid]Only a-z, 0-9 and - allowed")
        return value

    @staticmethod
    def ask_project_full_name():
        return Prompt.ask("[green]Project full name: (label) ")

    @staticmethod
    def ask_project_description():
        return Prompt.ask("[green]Project description")

    @staticmethod
    def ask_select_project(choices: list):
        return IntPrompt.ask(
            "[green]Select project above, pick the number", choices=choices
        )

    @staticmethod
    def ask_select_projects(choices: list):
        projects = []
        selected = KPrompt.ask(
            "[green]Select projects above, pick the numbers separated with comma",
            choices=choices,
        )
        for project in re.split(r",\s?", selected):
            projects.append(int(project))
        return projects

    @staticmethod
    def ask_select_project_task(choices: list):
        return IntPrompt.ask(
            "[green]Select task above, pick the number", choices=choices
        )

    @staticmethod
    def ask_confirm_create_project(client_name, project_name, project_label):
        return Confirm.ask(
            f"Are you sure you would like to create a project: {project_label} ({project_name}) for "
            f"client: {client_name}"
        )
