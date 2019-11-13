class Mail:
    raw_text: str

    def __init__(self, text: str, subject: str):
        self.raw_text = text
        self.subject = subject

    def __str__(self):
        return 'Subject: ' + self.subject + '\n' + self.raw_text
