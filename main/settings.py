import os
import sys

from config import settings
from main.file_io import FolderManager, YamlFileManager


class Settings:
    @staticmethod
    def get_default_setting(setting: str):
        settings_handle = FolderManager.get_settings_path()
        default_settings = YamlFileManager.read(settings_handle)
        if not setting in default_settings:
            sys.exit()
        return default_settings[setting]

    @staticmethod
    def get_default_settings(settings: [str] = None):
        settings_handle = FolderManager.get_settings_path()
        default_settings = YamlFileManager.read(settings_handle)
        if not settings:
            return default_settings
        merged_settings: [str] = []
        for setting in settings:
            if setting in default_settings:
                merged_settings.append(default_settings[setting])
        return merged_settings

    @staticmethod
    def get_setting(setting: str):
        return getattr(settings, setting)
