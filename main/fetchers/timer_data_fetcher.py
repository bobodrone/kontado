import os

from main.fetchers.data_fetcher import DataFetcher
from main.file_io import YamlFileManager, FileManager
from main.models.timer import Timer


class TimerDataFetcher(DataFetcher):
    def __init__(self):
        super().__init__()

    def read_data(self):
        timer_path = self.get_timer_path()
        if not FileManager.file_exist(timer_path):
            timer = Timer(
                client="",
                project="",
                task="",
                start=0,
                end=0,
                running=False,
                created=0,
                changed=0,
            )
            timer.write_to_file(timer_path)
        timer_yml = YamlFileManager.read(timer_path)
        return Timer.from_yaml(timer_yml)

    def get_timer_path(self):
        return f"{self.kontado_dir()}/config/timer.yml"
