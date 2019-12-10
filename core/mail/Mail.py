class Mail:
    def __init__(self, text: str, subject: str, sender: str):
        self.raw_text = text
        self.subject = subject
        self.sender = sender

    def __str__(self):
        return 'Subject: ' + self.subject + '\n' + 'Sender: ' + self.sender + '\n' + self.raw_text

    def get_raw_text(self):
        return self.raw_text

    def get_subject(self):
        return self.subject

    def get_from(self):
        return self.sender
