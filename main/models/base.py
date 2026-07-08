from dataclasses import dataclass
from main.file_io import YamlFileManager


@dataclass
class BaseModel:
    def to_yaml(self) -> dict:
        mydict = self.__dict__
        return mydict

    @staticmethod
    def from_yaml(class_yaml) -> any:
        return BaseModel()

    def write_to_file(self, filepath: str):
        yaml_dict = self.to_yaml()
        YamlFileManager.write(filepath, yaml_dict)

    @staticmethod
    def read_from_file(filepath: str, cls: any):
        object_yaml = YamlFileManager.read(filepath)
        return cls.from_yaml(object_yaml)
