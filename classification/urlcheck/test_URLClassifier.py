from unittest import TestCase

from classification.urlcheck.URLClassifier import URLClassifier


class TestURLClassifier(TestCase):

    def setUp(self) -> None:
        self.google_api_token = 'API_KEY'
        self.fixture = URLClassifier(None, None, None,
                      self)

    def test_check_urls(self):
        malware_ = 'http://malware.testing.google.test/testing/malware/'
        twitter = 'twitter.com'
        self.fixture.check_urls([malware_, twitter])
        self.assertTrue(self.fixture.checked_urls[malware_])
        self.assertFalse(self.fixture.checked_urls[twitter])

    def test_extract_url(self):
        self.assertEqual(self.fixture.url_extractor.find_urls('http://test.test.de')[0], 'test.test.de')
        self.assertFalse(self.fixture.url_extractor.has_urls('mailto:test@test.de'))
        self.assertFalse(self.fixture.url_extractor.has_urls('test@test.de'))
        self.assertEqual(self.fixture.url_extractor.find_urls('nonexistentprotocol:test.test.de')[0], 'test.test.de')
