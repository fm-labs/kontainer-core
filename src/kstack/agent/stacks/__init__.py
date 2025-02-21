import json
import os
from abc import ABCMeta, abstractmethod

from kstack.agent import settings


class ContainerStack(metaclass=ABCMeta):

    def __init__(self, name, meta=None):
        self.name = name
        self.project_dir = os.path.join(settings.AGENT_DATA_DIR, 'stacks', self.name)
        self.project_file = os.path.join(settings.AGENT_DATA_DIR, 'stacks', self.name + '.stack.json')
        self.managed = True

        self._meta = meta


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

    def load(self) -> None:
        with open(self.project_file, "r") as f:
            self._meta = json.load(f)

    def dump(self) -> None:
        with open(self.project_file, "w") as f:
            json.dump(self._meta, f, indent=2)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "project_dir": self.project_dir,
            "managed": self.managed,
            "meta": self.meta
        }

    def to_dict(self):
        return self.serialize()

