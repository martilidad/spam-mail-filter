from unittest import TestCase

from util.EnronDataset import EnronDataset


class TestEnronDataset(TestCase):

    def test_load(self):
        data = EnronDataset()
        loaded_data = data.load_files()
        self.assertGreater(len(loaded_data.keys()), 1)
