import os

from main.services.service import Service


class GitService(Service):
    def __init__(self):
        super().__init__()

    def git_add(self, file: str):
        os.system(f"git add {file}")

    def git_commit(self, message: str):
        os.system(f'git commit -m "{message}"')
