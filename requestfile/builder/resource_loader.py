import os
from abc import ABCMeta, abstractmethod


class BaseResourceLoader(metaclass=ABCMeta):
    @abstractmethod
    def read_bytes(self, path: str) -> bytes:
        pass


class ResourceLoader(BaseResourceLoader):
    """Load data from files"""

    def __init__(self, root: str):
        self.root = root

    def read_bytes(self, path: str):
        if not os.path.isabs(path):
            path = os.path.join(self.root, path)
        with open(path, "rb") as fp:
            return fp.read()


class TestingResourceLoader(BaseResourceLoader):
    def __init__(self):
        self.files: dict[str, bytes] = {}

    def read_bytes(self, path: str) -> bytes:
        return self.files[path]
