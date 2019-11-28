from unittest import TestCase

from classification.urlcheck.URLClassifier import URLClassifier


class TestURLClassifier(TestCase):
    def test_check_urls(self):
        classifier = URLClassifier(None, None, None,
                                   'AIzaSyBbgFpLOjHB16iByVzrRmk_RyeCttN2_3A')
        malware_ = 'http://malware.testing.google.test/testing/malware/'
        twitter = 'twitter.com'
        classifier.check_urls([malware_, twitter])
        self.assertTrue(classifier.checked_urls[malware_])
        self.assertFalse(classifier.checked_urls[twitter])

    def test_extract_url(self):
        classifier = URLClassifier(None, None, None,
                                   'AIzaSyBbgFpLOjHB16iByVzrRmk_RyeCttN2_3A')
        result = classifier.url_extractor.find_urls(
            "This is my tweet check it out http://example.com/blah twitter.com "
            "http://google.com https://thi.de test.nz")
        self.assertIn('http://example.com/blah', result)
        self.assertIn('twitter.com', result)
        self.assertIn('http://google.com', result)
        self.assertIn('https://thi.de', result)
        self.assertIn('test.nz', result)
