import os
from abc import abstractmethod

import sklearn.datasets as datasets


class Dataset:
    """Abstract Dataset class"""
    categories = ["ham", "spam"]
    preload = True

    def container_path(self):
        return os.path.abspath(
            os.path.dirname(__file__) + '/../../data/' +
            self.relative_container_path)

    def load_files(self):
        return datasets.load_files(container_path=self.container_path(),
                                   categories=self.categories,
                                   load_content=self.preload)

    @property
    @abstractmethod
    def relative_container_path(self):
        pass
