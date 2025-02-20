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
        return f"ContainerStack: {self.name}"

    @property
    def meta(self):
        if self._meta is None:
            self.load()
        return self._meta

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def load(self):
        with open(self.project_file, "r") as f:
            self._meta = json.load(f)

    def dump(self):
        with open(self.project_file, "w") as f:
            json.dump(self._meta, f, indent=2)

    def serialize(self):
        return {
            "name": self.name,
        }

    def to_dict(self):
        return self.serialize()

