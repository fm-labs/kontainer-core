
from abc import ABCMeta, abstractmethod

class ContainerStack(metaclass=ABCMeta):

    def __init__(self, name):
        self.name = name

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

    def serialize(self):
        return {
            "name": self.name,
        }