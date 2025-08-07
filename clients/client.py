"""
Client interface for the Euler system.
"""

from abc import ABC, abstractmethod


class Client(ABC):
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
