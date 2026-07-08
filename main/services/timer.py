import os
import math
import sys

from config import settings
from main.fetchers.data_fetcher import DataFetcher
from main.file_io import FileIO
from datetime import datetime

from main.models.timer import Timer
from main.services.service import Service


class TimerService(Service):
    timer: Timer

    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher
        self.timer = None

    def time_check_running_timer(self) -> bool:
        timer = self.get_timer(no_cache=True)
        if timer and timer.running is True:
            return True
        return False

    def get_timer(self, no_cache=False) -> Timer:
        if self.timer and not no_cache:
            return self.timer
        timer = self.fetcher.read_data()
        if timer:
            self.timer = timer
        return timer

    def time_start_timer(self, client, project, task) -> None:
        timer = self.get_timer(no_cache=True)
        if timer.running:
            print("Timer can not be started since it is already running.")
            sys.exit()
        timer = self.get_timer()
        timer.running = True
        timer.start = self.time_current_time()
        timer.end = 0
        timer.client = client
        timer.project = project
        timer.task = task.type
        timer_handle = self.fetcher.get_timer_path()
        timer.write_to_file(timer_handle)

    def time_stop_timer(self) -> None:
        if not self.time_check_running_timer():
            print("Timer can not be stopped since it is not running.")
            exit()
        timer_handle = self.fetcher.get_timer_path()
        timer = self.get_timer()
        timer.running = False
        timer.end = self.time_current_time()
        timer.write_to_file(timer_handle)

    @staticmethod
    def time_current_time() -> int:
        return int(datetime.timestamp(datetime.now()))

    @staticmethod
    def time_ts2date(ts) -> datetime:
        return datetime.fromtimestamp(ts, tz=None)

    @staticmethod
    def time_calculate_time_difference(start, stop) -> str:
        hours = 0
        seconds: int = int(stop) - int(start)
        minutes: int = seconds // 60
        seconds: int = seconds % 60
        if minutes > 59:
            minutes = minutes % 60
            hours = minutes // 60
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    @staticmethod
    def time_round_up_to_closest(hours: float):
        return (
            math.ceil(hours * settings.DEFAULT_RATE_ROUND_UP)
            / settings.DEFAULT_RATE_ROUND_UP
        )
