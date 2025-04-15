import json
import os
from abc import ABCMeta, abstractmethod

from kontainer import settings


class ContainerStack(metaclass=ABCMeta):

    def __init__(self, name, managed=False, meta=None):
        self.name = name
        self.managed = managed
        self.project_dir = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', self.name)
        self.project_file = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', self.name + '.stack.json')

        self._meta = meta

        if not managed:
            self.project_dir = None
            self.project_file = None
            #self._meta = {}

    def __str__(self):
        return f"Stack: {self.name}"

    @property
    def meta(self) -> dict:
        if self._meta is None:
            self.load()
        return self._meta

    @abstractmethod
    def up(self) -> bytes:
        pass

    @abstractmethod
    def down(self) -> bytes:
        pass

    @abstractmethod
    def stop(self) -> bytes:
        pass

    @abstractmethod
    def restart(self) -> bytes:
        pass

    @abstractmethod
    def destroy(self) -> bytes:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    def load(self) -> None:
        if not self.managed:
            #print(f"Stack {self.name} is not managed")
            return

        with open(self.project_file, "r") as f:
            self._meta = json.load(f)

    def dump(self) -> None:
        if not self.managed:
            #print(f"Stack {self.name} is not managed")
            return

        with open(self.project_file, "w") as f:
            json.dump(self._meta, f, indent=2)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "project_dir": self.project_dir,
            "project_file": self.project_file,
            "managed": self.managed,
            "meta": self.meta
        }

    def to_dict(self):
        return self.serialize()

