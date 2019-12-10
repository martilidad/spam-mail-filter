from unittest import TestCase

from core.config.Config import Config


class TestConfig(TestCase):
    def test_load(self):
        Config()
