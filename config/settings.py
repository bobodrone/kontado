from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_FOLDER = BASE_DIR / "config"
CLIENTS_FOLDER = BASE_DIR / "clients"
DEFAULTS_FOLDER = BASE_DIR / "defaults"

INVOICE_NAME_PATTERN = "{{ client }}-{{ Y }}-{{ nnnn }}"
LINE_ITEM_PATTERN = "{{ client }}-{{ Ymd }}-{{ nnnn }}"

DEFAULT_RATE_NTH = 1
DEFAULT_RATE_TYPE = "hour"
DEFAULT_RATE_AMOUNT = 100000
DEFAULT_RATE_CURRENCY = "SEK"
DEFAULT_RATE_VAT = 25
# 1 = round up to nearest 1 (Full hour)
# 2 = round up to nearest 0.5 (Half hour/30 min)
# 4 = round up to nearest 0.25 (Quarter ov an hour/15min)
DEFAULT_RATE_ROUND_UP = 4


DEFAULT_TASKS = [
    {
        "label": "Development",
        "type": "development",
        "default": True,
        "rate": {"amount": 100000, "currency": "SEK", "type": "hourly", "vat": 25},
    },
    {
        "label": "Administration",
        "type": "administration",
        "default": False,
        "rate": {"amount": 100000, "currency": "SEK", "type": "hourly", "vat": 25},
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
