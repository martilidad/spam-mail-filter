import logging

from pysafebrowsing import SafeBrowsing
from urlextract import URLExtract

from classification.DelegatableClassifier import DelegatableClassifier
from core.Mail import Mail
from core.MailAttributes import MailAttributes
from core.Serializable import T


class URLClassifier(DelegatableClassifier):
    def __init__(self, train_mails: [Mail], train_labels: [int],
                 target_attribute: MailAttributes, config):
        api_token = config.google_api_token
        if api_token is None:
            logging.fatal("Google API Token is not set. Unable to initialize URLClassifier.")
            raise ValueError("Google API Token is not set. Unable to initialize URLClassifier.")
        self.target_attribute = target_attribute
        self.safe_browsing = SafeBrowsing(api_token)
        self.url_extractor = URLExtract()
        self.checked_urls = {}

    def train(self, mails: [Mail] = None, labels: [int] = None):
        pass

    def classify(self, mails: [Mail]) -> [float]:
        mail_dict = {}
        new_urls = []
        for mail in mails:
            text = self.target_attribute(mail)
            urls = self.url_extractor.find_urls(text)
            new_urls = [*new_urls, *self.filter_new(urls)]
            mail_dict[mail] = urls
        # empty list is false
        if new_urls:
            self.check_urls(new_urls)
        # checked urls should now contain every url
        # check if any url in each mail is malicious
        # float(True) is 1 float(False) is 0
        return [
            float(any(self.checked_urls[url] for url in mail_dict[mail]))
            for mail in mails
        ]

    def check_urls(self, urls: [str]):
        response = self.safe_browsing.lookup_urls(urls)
        for url in urls:
            self.checked_urls[url] = response[url]['malicious']

    @property
    def save_folder(self):
        return None

    def serialize(self, sub_folder: str = None):
        pass

    def deserialize(self, sub_folder: str = None) -> T:
        return self

    def filter_new(self, urls):
        new_urls = []
        for url in urls:
            if self.checked_urls.get(url) is None:
                new_urls = [*new_urls, url]
        return new_urls
