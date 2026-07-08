from dataclasses import dataclass
from datetime import datetime
from main.models.base import BaseModel


@dataclass
class Timer(BaseModel):
    client: str
    project: str
    task: str
    start: int
    end: int
    running: bool
    created: int
    changed: int

    @staticmethod
    def get_defaults():
        curr_dt = datetime.now()
        created = int(round(curr_dt.timestamp()))
        return {
            "client": "",
            "project": "",
            "task": "",
            "start": 0,
            "end": 0,
            "running": False,
            "created": created,
            "changed": created,
        }

    @staticmethod
    def from_yaml(timer_yaml) -> any:
        curr_dt = datetime.now()
        created = int(round(curr_dt.timestamp()))
        return Timer(
            client=timer_yaml["client"],
            project=timer_yaml["project"],
            task=timer_yaml["task"],
            start=timer_yaml["start"],
            end=timer_yaml["end"],
            running=timer_yaml["running"],
            created=created,
            changed=created,
        )
