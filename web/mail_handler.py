import smtplib

from email.mime.text import MIMEText

class Mail:
    def __init__(self, to, link):
        self.to = to
        self.link = link

    def send(self):
        msg = "Hi,\n\nYou requested to change the password for your SPOT* account. " \
              "Please click on the link below to choose a new password. If you did " \
              "not trigger the change, you can ignore this message\n\n"
        msg += self.link
        msg += "\n\nRegards,\nISS4E Lab"
        msg = MIMEText(msg)
        from_address = "spot@blizzard.cs.uwaterloo.ca"
        msg['Subject'] = 'SPOT* Change Password Request'
        msg['From'] = from_address
        msg['To'] = self.to
        s = smtplib.SMTP('localhost')
        s.sendmail(from_address, self.to, msg.as_string())
        s.quit()
