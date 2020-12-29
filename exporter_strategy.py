from abc import ABC, abstractmethod


class ExportingStrategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def do_export(self) -> list:
        pass
