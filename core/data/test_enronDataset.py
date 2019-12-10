from unittest import TestCase

from core.data.EnronDataset import EnronDataset


class TestEnronDataset(TestCase):
    def test_load(self):
        data = EnronDataset()
        loaded_data = data.load_files()
        self.assertGreater(len(loaded_data.keys()), 1)
