import json
from email.mime.text import MIMEText
import smtplib


class EmailReminder(object):
    def __init__(self, args):
        self.reminder = args['reminder']
        self.user = args['user']
        self.settings = args['settings']

        self.mailserver = smtplib.SMTP(self.settings['email.server'],
                                       self.settings['email.port'])
        self.mailserver.ehlo()
        self.mailserver.starttls()
        self.mailserver.ehlo()
        self.mailserver.login(self.settings['email.username'],
                              self.settings['email.password'])

    def send_reminder(self):
        # Create a text/plain message
        msg = MIMEText(self.reminder['description'])

        msg['Subject'] = self.reminder['title']
        msg['From'] = self.settings['email.username']
        msg['To'] = self.user['email']

        self.mailserver.sendmail(self.settings['email.username'],
                            [self.user['email']], msg.as_string())
        self.mailserver.quit()
