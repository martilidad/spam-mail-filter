import sklearn.datasets as datasets
import os


class Dataset:
    """Abstract Dataset class"""

    relative_container_path = ""
    categories = ["ham", "spam"]
    preload = True

    def container_path(self):
        return os.path.abspath(
            os.path.dirname(__file__) + '/../data/' +
            self.relative_container_path)

    def load_files(self):
        return datasets.load_files(container_path=self.container_path(),
                                   categories=self.categories,
                                   load_content=self.preload)
