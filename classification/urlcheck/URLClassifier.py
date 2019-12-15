import logging
from typing import List, Set

import numpy as np
from pysafebrowsing import SafeBrowsing
from urlextract import URLExtract

from classification.DelegatableClassifier import DelegatableClassifier
from core.mail.Mail import Mail
from core.mail.MailAttributes import MailAttributes
from util.Serializable import Serializable


class URLClassifier(DelegatableClassifier, Serializable['URLClassifier']):
    def __init__(self, train_mails: List[Mail], train_labels: List[int],
                 target_attribute: MailAttributes, config):
        super().__init__(train_mails, train_labels, target_attribute, config)
        api_token = config.google_api_token
        if api_token is None:
            logging.fatal(
                "Google API Token is not set. Unable to initialize URLClassifier."
            )
            raise ValueError(
                "Google API Token is not set. Unable to initialize URLClassifier."
            )
        self.target_attribute = target_attribute
        self.safe_browsing = SafeBrowsing(api_token)
        self.url_extractor = URLExtract()
        self.url_extractor.extract_email = False
        self.url_extractor.get_stop_chars_left().add(':')
        self.checked_urls: dict = {}

    def train(self, mails: List[Mail] = None, labels: List[int] = None):
        pass

    def classify(self, mails: List[Mail]) -> List[float]:
        mail_dict: dict = {}
        new_urls: set = set()
        for mail in mails:
            text = self.target_attribute(mail)
            urls = set(self.url_extractor.find_urls(text, only_unique=True))
            new_urls.update(self.filter_new(urls))
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

    def check_urls(self, urls: Set[str]):
        # api only supports 500 urls at a time
        needed_parts = int(len(urls) / 500) + 1
        response: dict = {}
        for batch in np.array_split(list(urls), needed_parts):
            try:
                response.update(self.safe_browsing.lookup_urls(batch))
            except KeyError as ex:
                # catch exception for bug in safe_browsing module
                if ex.args[0] == 'details':
                    for url in batch:
                        response.update({url: {"malicious": False}})
                else:
                    raise ex
        for url in urls:
            self.checked_urls[url] = response[url]['malicious']

    @property
    def save_folder(self):
        return None

    def serialize(self, sub_folder: str = None):
        pass

    def deserialize(self, sub_folder: str = None) -> 'URLClassifier':
        return self

    def filter_new(self, urls: set) -> set:
        new_urls: set = set()
        for url in urls:
            if self.checked_urls.get(url) is None:
                new_urls.add(url)
        return new_urls
