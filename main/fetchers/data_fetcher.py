import os
from typing import Protocol
from main.file_io import FileManager


class DataFetcher(Protocol):
    def read_data(self):
        ...

    def kontado_dir(self):
        return FileManager.get_kontado_dir()

    def current_path(self):
        return os.getcwd()

    def join_path(self, parts: list):
        return os.path.join(*parts)
