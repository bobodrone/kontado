import os
from typing import List

import yaml


class FileManager:
    @staticmethod
    def file_exist(file: str):
        return os.path.isfile(file)

    @staticmethod
    def create(file_name: str, content: str):
        with open(file_name, "w") as f:
            f.write(content)

    @staticmethod
    def get_kontado_dir():
        file_name = ".kontado"
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        if os.path.exists(os.path.join(current_dir, file_name)):
            return current_dir
        elif parent_dir and os.path.exists(os.path.join(parent_dir, file_name)):
            return parent_dir
        else:
            search_dir = parent_dir
            while search_dir and search_dir != os.path.dirname(search_dir):
                if os.path.exists(os.path.join(search_dir, file_name)):
                    return search_dir
                else:
                    search_dir = os.path.dirname(search_dir)

    @staticmethod
    def move_file(file: str, destination: str):
        return os.rename(file, destination)


class FolderManager:
    @staticmethod
    def get_settings_path():
        return FolderManager.join_path(
            [FolderManager.get_config_folder_path(), "settings.yml"]
        )

    @staticmethod
    def get_config_folder_path():
        return FolderManager.join_path([FileManager.get_kontado_dir(), "config"])

    @staticmethod
    def folder_exist(folder: str):
        return os.path.isdir(folder)

    @staticmethod
    def create_folder(folder: str):
        os.mkdir(folder)

    @staticmethod
    def join_path(parts: list):
        return os.path.join(*parts)

    @staticmethod
    def iterate(folder: str, is_file: bool = False):
        items = []
        with os.scandir(folder) as iterator:
            for entry in iterator:
                if is_file:
                    if not entry.name.startswith(".") and entry.is_file():
                        items.append(entry)
                else:
                    if not entry.name.startswith(".") and not entry.is_file():
                        items.append(entry)
        return items

    @staticmethod
    def iterate_sub_folders(main_folder: str, sub_folders=None, is_file: bool = False):
        if sub_folders is None:
            sub_folders = []
        items = []
        if os.path.isdir(main_folder):
            for directory in sub_folders:
                with os.scandir(directory) as iterator:
                    for entry in iterator:
                        if is_file:
                            if not entry.name.startswith(".") and entry.is_file():
                                items.append(entry)
                        else:
                            if not entry.name.startswith(".") and not entry.is_file():
                                items.append(entry)
        return items


class YamlFileManager:
    @staticmethod
    def read(file_path):
        with open(file_path) as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def write(file_path, yaml_dict):
        with open(file_path, "w") as file:
            try:
                yaml.dump(yaml_dict, file)
            except yaml.YAMLError as exc:
                print(exc)


class FileIO:
    """File Io class handle input och output of files"""

    @staticmethod
    def clone_default_yaml_file(default_path, file_path, yaml_dict):
        defaults = FileIO.read_yaml_file(default_path)
        defaults["client"].update({"name": yaml_dict["name"]})
        defaults["client"].update({"label": yaml_dict["label"]})
        defaults["client"].update({"description": yaml_dict["label"]})
        defaults["client"]["company_info"].update({"name": yaml_dict["label"]})
        FileIO.save_yaml_file(file_path, defaults)

    @staticmethod
    def read_yaml_file(file_path):
        with open(file_path) as file:
            try:
                yaml_dict = yaml.safe_load(file)
                return yaml_dict
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def create_client_folder(path):
        os.mkdir(path)

    @staticmethod
    def save_yaml_file(file_path, yaml_dict):
        with open(file_path, "w") as file:
            try:
                yaml.dump(yaml_dict, file)
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def delete_yaml_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"The file {file_path} does not exist")
