from config import settings


class BaseProcessor:
    def __init__(self):
        self.settings = settings

    def get_setting(self, setting: str):
        return getattr(self.settings, setting)
