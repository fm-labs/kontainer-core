import json
import os
from abc import ABCMeta, abstractmethod

from kontainer import settings


class ContainerStack(metaclass=ABCMeta):

    def __init__(self, name, ctx_id, managed=False, config=None):
        self.ctx_id = ctx_id
        self.name = name
        self.managed = managed
        #self.project_dir = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', self.ctx_id, self.name)
        self.project_dir = f"stacks/{self.ctx_id}/{self.name}"

        #self._config_file = os.path.join(settings.KONTAINER_DATA_DIR, 'stacks', self.ctx_id, self.name + '.stack.json')
        self._config_file = f"stacks/{self.ctx_id}/{self.name}.stack.json"
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

    @abstractmethod
    def exists(self) -> bool:
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

        # serialized = {}
        # if self.meta:
        #     serialized = self.meta.copy()
        #
        # serialized["ctx_id"] = self.ctx_id
        # serialized["name"] = self.name
        # serialized["managed"] = self.managed
        # serialized["project_dir"] = self.project_dir
        # serialized["project_file"] = self.project_file
        # return serialized

    def to_dict(self):
        return self.serialize()

