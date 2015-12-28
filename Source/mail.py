import smtplib
from email.mime.text import MIMEText
from time import sleep


# A simple email class. 

class Mail:

    def __init__(self):
        self.emailAddr = 'shylock2105@gmail.com'
        self.emailPassword = 'raspberrypi'

    def send_email(self, text, subject, to='derrick2105@gmail.com'):
        msg = MIMEText(text)
        msg['Subject'] = subject
        msg['From'] = self.emailAddr
        msg['To'] = to

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        login = False
        while not login:
            try:
                s.login(self.emailAddr, self.emailPassword)
                login = True
            except smtplib.SMTPAuthenticationError:
                login = False
                sleep(5)
        s.sendmail(self.emailAddr, [to], msg.as_string())
        s.quit()
