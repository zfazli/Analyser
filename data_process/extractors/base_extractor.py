from abc import ABC, abstractmethod


class BaseExtractor(ABC):

    def __init__(self, name):

        self.name = name

    @abstractmethod
    def update(self, edge):
        """
        Called for every edge.
        """
        pass

    @abstractmethod
    def finalize(self):
        """
        Return pandas dataframe.
        """
        pass