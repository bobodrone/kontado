from dataclasses import dataclass
from datetime import datetime
from main.models.rate import Rate
from main.settings import Settings
from main.models.base import BaseModel
from main.models.task import Task


@dataclass
class Project(BaseModel):
    name: str
    label: str
    description: str
    client: str
    tasks: [Task]
    created: int
    changed: int

    @staticmethod
    def get_defaults(client: str):
        default_tasks = Settings.get_default_setting("default_tasks")
        return {
            "name": "my_project",
            "label": "My project",
            "description": "My project to save the earth.",
            "client": client,
            "tasks": default_tasks,
        }

    def to_yaml(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_yaml(project_yaml) -> any:
        curr_dt = datetime.now()
        created = int(round(curr_dt.timestamp()))
        return Project(
            name=project_yaml["name"],
            label=project_yaml["label"],
            description=project_yaml["description"],
            client=project_yaml["client"],
            tasks=[
                Task(
                    type=task["type"],
                    default=task["default"],
                    label=task["label"],
                    rate=Rate(
                        amount=task["rate"]["amount"],
                        currency=task["rate"]["currency"],
                        type=task["rate"]["type"],
                        vat=task["rate"]["vat"],
                    ),
                )
                for task in project_yaml["tasks"]
            ],
            created=created,
            changed=created,
        )
