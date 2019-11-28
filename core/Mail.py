class Mail:
    def __init__(self, text: str, subject: str):
        self.raw_text = text
        self.subject = subject

    def __str__(self):
        return 'Subject: ' + self.subject + '\n' + self.raw_text

    def get_raw_text(self):
        return self.raw_text

    def get_subject(self):
        return self.subject
