"""Handle init commands"""
import sys
import os
import subprocess
from datetime import datetime
from rich.prompt import Confirm, Prompt
from main.models.company_info import CompanyInfo
from main.models.address import Address
from main.models.contact import Contact
from main.file_io import FileManager, FolderManager
from main.formatters.formatters import MessageFormatter
from main.models.settings import Settings
from main.models.task import Task
from main.models.timer import Timer
from main.models.me import Me


def initialize():
    """Init a local project that creates all default folders and files"""

    curr_dt = datetime.now()
    created = int(round(curr_dt.timestamp()))
    current_folder = os.getcwd()

    folder_name = Prompt.ask(
        "What folder name would you like to have?", default="kontado"
    )
    kontado_folder = FolderManager.join_path([current_folder, folder_name])

    if FolderManager.folder_exist(kontado_folder):
        MessageFormatter().error("There are already a folder called kontado there!")
        sys.exit()

    confirm = Confirm.ask(
        f"Are you sure you would like to create a Kontado folder here: {kontado_folder}"
    )
    if not confirm:
        sys.exit()

    # Create main folder for kontado as well as its two subfolders: config and clients.
    FolderManager.create_folder(kontado_folder)
    kontado_dot_file = FolderManager.join_path([kontado_folder, ".kontado"])
    FileManager.create(kontado_dot_file, f"Created: {created}")
    config_folder = FolderManager.join_path([kontado_folder, "config"])
    clients_folder = FolderManager.join_path([kontado_folder, "clients"])
    FolderManager.create_folder(config_folder)
    FolderManager.create_folder(clients_folder)

    # Create all config yml files in the config folder
    initialize_config(config_folder, created)

    # Initialize a clean git repository
    confirm = Confirm.ask("Do you want me to initialize a GIT repository for you?")
    if confirm:
        subprocess.run(
            f"cd {kontado_folder} && git init",
            shell=True,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            f"cd {kontado_folder} && echo 'config/timer.yml' > .gitignore",
            shell=True,
            capture_output=True,
            check=True,
        )


def initialize_config(config_folder: str, created: int):
    """Handle all creation of config files"""
    timer_handle = FolderManager.join_path([config_folder, "timer.yml"])
    initialize_config_timer(timer_handle, created)

    settings_handle = FolderManager.join_path([config_folder, "settings.yml"])
    initialize_config_settings(settings_handle, created)

    me_handle = FolderManager.join_path([config_folder, "me.yml"])
    initialize_config_me(me_handle, created)


def initialize_config_timer(timer_handle: str, created: int):
    """Handle creation of Timer class yml file"""
    timer = Timer(
        client="",
        project="",
        task="",
        start=0,
        end=0,
        running=False,
        created=created,
        changed=created,
    )
    timer.write_to_file(timer_handle)


def initialize_config_settings(settings_handle: str, created: int):
    """Handle creation of Settings class yml file"""
    defaults = Settings.get_defaults()
    settings = Settings(
        invoice_name_pattern=defaults["invoice_name_pattern"],
        line_item_pattern=defaults["line_item_pattern"],
        default_rate_nth=defaults["default_rate_nth"],
        default_rate_type=defaults["default_rate_type"],
        default_rate_amount=defaults["default_rate_amount"],
        default_rate_currency=defaults["default_rate_currency"],
        default_rate_vat=defaults["default_rate_vat"],
        default_rate_round_up=defaults["default_rate_round_up"],
        default_tasks=Task.get_defaults(
            defaults["default_rate_amount"], defaults["default_rate_vat"]
        ),
        created=created,
        changed=created,
    )
    settings.write_to_file(settings_handle)


def initialize_config_me(me_handle: str, created: int):
    """Handle creation of Me class yml file"""
    defaults = Me.get_defaults()
    me_data = Me(
        name=defaults["name"],
        label=defaults["label"],
        language=defaults["language"],
        description=defaults["description"],
        company_info=CompanyInfo(
            name=defaults["company_info"]["name"],
            orgnr=defaults["company_info"]["orgnr"],
            vatnr=defaults["company_info"]["vatnr"],
            postal_address=Address(
                co=defaults["company_info"]["postal_address"]["co"],
                thoroughfare=defaults["company_info"]["postal_address"]["thoroughfare"],
                premise=defaults["company_info"]["postal_address"]["premise"],
                postalcode=defaults["company_info"]["postal_address"]["postalcode"],
                locality=defaults["company_info"]["postal_address"]["locality"],
                region=defaults["company_info"]["postal_address"]["region"],
                country=defaults["company_info"]["postal_address"]["country"],
            ),
            visitor_address=Address(
                co=defaults["company_info"]["visitor_address"]["co"],
                thoroughfare=defaults["company_info"]["visitor_address"][
                    "thoroughfare"
                ],
                premise=defaults["company_info"]["visitor_address"]["premise"],
                postalcode=defaults["company_info"]["visitor_address"]["postalcode"],
                locality=defaults["company_info"]["visitor_address"]["locality"],
                region=defaults["company_info"]["visitor_address"]["region"],
                country=defaults["company_info"]["visitor_address"]["country"],
            ),
        ),
        contacts=[
            Contact(
                person=defaults["contacts"][0]["person"],
                title=defaults["contacts"][0]["title"],
                email=defaults["contacts"][0]["email"],
                phone=defaults["contacts"][0]["phone"],
            )
        ],
        last_invoice=0,
        payment_options=[],
        created=created,
        changed=created,
    )
    me_data.write_to_file(me_handle)


def main():
    """Handle the whole initialize setup"""
    initialize()


if __name__ == "__main__":
    main()
