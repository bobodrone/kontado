import sys
from datetime import datetime

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager
from main.formatters.formatters import MessageFormatter
from main.models.me import Me
from main.services.service import Service


class MeService(Service):
    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher

    def get_me(self, no_cache=False) -> Me:
        me = self.fetcher.read_data()
        return me
