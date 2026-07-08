from dataclasses import dataclass
from main.models.base import BaseModel
from main.models.task import Task


@dataclass(order=True)
class Settings(BaseModel):
    invoice_name_pattern: str
    line_item_pattern: str
    default_rate_nth: int
    default_rate_type: str
    default_rate_amount: int
    default_rate_currency: str
    default_rate_vat: int
    default_rate_round_up: int
    default_tasks: [Task]
    created: int
    changed: int

    @staticmethod
    def get_defaults():
        return {
            "invoice_name_pattern": "{{ client }}-{{ Y }}-{{ nnnn }}",
            "line_item_pattern": "{{ client }}-{{ Ymd }}-{{ nnnn }}",
            "default_rate_nth": 1,
            "default_rate_type": "hour",
            "default_rate_amount": 100000,
            "default_rate_currency": "SEK",
            "default_rate_vat": 25,
            "default_rate_round_up": 4,
        }


# 1 = round up to nearest 1 (Full hour)
# 2 = round up to nearest 0.5 (Half hour/30 min)
# 4 = round up to nearest 0.25 (Quarter ov an hour/15min)


DEFAULT_TASKS = [
    {
        "label": "Development",
        "type": "development",
        "default": True,
        "rate": {"amount": 900, "currency": "SEK", "type": "hourly", "vat": 25},
    },
    {
        "label": "Administration",
        "type": "administration",
        "default": False,
        "rate": {"amount": 900, "currency": "SEK", "type": "hourly", "vat": 25},
    },
    {
        "label": "Development (Free)",
        "type": "development-free",
        "default": False,
        "rate": {"amount": 0, "currency": "SEK", "type": "free", "vat": 0},
    },
    {
        "label": "Administration (Free)",
        "type": "administration-free",
        "default": False,
        "rate": {"amount": 0, "currency": "SEK", "type": "free", "vat": 0},
    },
]
