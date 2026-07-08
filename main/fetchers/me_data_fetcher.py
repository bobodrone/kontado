import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FolderManager, YamlFileManager
from main.models.me import Me


class MeDataFetcher(DataFetcher):
    def read_data(self):
        me_path = self.get_me_path()
        me_yml = YamlFileManager.read(me_path)
        me = Me.from_yaml(me_yml)
        return me

    def get_me_path(self):
        return f"{self.kontado_dir()}/config/me.yml"
