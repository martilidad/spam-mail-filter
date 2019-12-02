import os

from core.Dataset import Dataset
from core.Mail import Mail

LINESEP = os.linesep.encode()
SUBJECT_PREFIX = "Subject: "


class EnronDataset(Dataset):
    relative_container_path = "ENRON/"

    @staticmethod
    def enron_string_to_mail(text: str):
        subject = SUBJECT_PREFIX
        stop = text.find(LINESEP)
        return Mail(text[stop + len(LINESEP):], text[len(subject):stop], None)
