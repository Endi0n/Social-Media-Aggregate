class FakeMail:

    def __init__(self, app):
        self.default_sender = 'None'
        self.ascii_attachments = None

        app.extensions['mail'] = self

    def send(self, message):
        message.recipients = ['None']

        print('<MailBegin>')
        print(f"{message.subject} Recipients: {' '.join(message.recipients)}")
        print(message)
        print('<EndMail>')
