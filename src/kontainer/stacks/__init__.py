import json
import os
from abc import ABCMeta, abstractmethod

from kontainer import settings


class ContainerStack(metaclass=ABCMeta):
    """
    Base class for all container stacks.

    This class is used to manage the lifecycle of a stack, including
    starting, stopping, and destroying the stack. It also provides
    methods for loading and dumping the stack configuration.

    Attributes:
        ctx_id (str): The context ID of the stack.
        name (str): The name of the stack.
        managed (bool): Whether the stack is managed by the system.
        project_dir (str): The directory where the stack is located.
        _config_file (str): The path to the stack configuration file.
        _config (dict): The stack configuration.
    """

    def __init__(self, name, ctx_id, managed=False, config=None):
        self.ctx_id = ctx_id
        self.name = name
        self.managed = managed
        #self.project_dir = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', self.ctx_id, self.name)
        self.project_dir = f"stacks/{self.ctx_id}/{self.name}"

        self._config_file = os.path.join(settings.KONTAINER_DATA_DIR, f"stacks/{self.ctx_id}/{self.name}.stack.json")
        self._config = config

        if not managed:
            self.project_dir = None
            self._config_file = None
            #self._config = None

    def __str__(self):
        return f"Stack: {self.name}"

    @property
    def config(self) -> dict:
        if self._config is None:
            self.load()
        return self._config

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
        if not self.managed:
            #print(f"Stack {self.name} is not managed")
            return

        with open(self._config_file, "r") as f:
            self._config = json.load(f)

    def dump(self) -> None:
        if not self.managed:
            #print(f"Stack {self.name} is not managed")
            return

        with open(self._config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def serialize(self) -> dict:
        return {
            "ctx_id": self.ctx_id,
            "name": self.name,
            "project_dir": self.project_dir,
            "managed": self.managed,
            "config": self.config
        }

    def to_dict(self):
        return self.serialize()
