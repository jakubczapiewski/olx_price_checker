import json
import logging
import os
import smtplib
import ssl
import threading
import time

from main import main


class SMTPServer:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.__port = 465
        self.__smtp_server = "smtp.gmail.com"  # server
        self.__sender_email = ""  # sender mail
        self.__password = ""  # password
        self.__context = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL()
        self.lock = threading.Lock()
        self.log = logging.Logger('mail_server ')

        h = logging.FileHandler(f'{BASE_DIR}/logs.txt')
        h.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

        self.log.addHandler(h)

    def login(self):
        with self.lock:
            try:
                mail = self.server.ehlo()
                return
            except:
                try:
                    self.server = smtplib.SMTP_SSL(self.__smtp_server, self.__port, context=self.__context)
                    self.server.login(self.__sender_email, self.__password)
                except:
                    self.log.error('login problems')
                    return
            self.log.info('successfully login')

    def send(self, receiver_email, message):
        with self.lock:
            self.server.sendmail(self.__sender_email, receiver_email, message)


class ContinuousWork:
    lock = threading.Lock()
    check_offers = set()

    def __init__(self, client_id: str, client_secret: str, recipients: list, cycle_time_m: float or int = 5):
        self.client_id = client_id
        self.client_secret = client_secret
        self.recipients = recipients
        self.cycle_time_s = cycle_time_m * 60
        self.smtp_server = SMTPServer()

    def run(self):
        while True:
            try:
                result = main(
                    self.client_id,
                    self.client_secret,
                    only_profitable=True,
                    request_per_minute_olx=120,
                    offer_check_function=ContinuousWork.is_offer_check
                )
                for offer in result.items():
                    self.send_mail(offer)
            except:
                logging.error('problems with main')
            time.sleep(self.cycle_time_s)

    @staticmethod
    def is_offer_check(offer: str):
        result = not (offer in ContinuousWork.check_offers)
        ContinuousWork.check_offers.add(offer)
        return result

    def send_mail(self, offer):
        components = json.dumps(offer[1], indent=4)
        message: str = f'''Subject: \n
               Nowe obiecujące ogłoszenie \n
                
                Link:{offer[0]} \n
                Components{components} \n

               '''

        self.smtp_server.login()
        for receiver in self.recipients:
            self.smtp_server.send(receiver, message.encode('utf-8'))


if __name__ == '__main__':
    client_id = ""  # client id
    client_secret = ""  # client secret
    recipients = [
        'mail@server.com'
    ]
    continuous = ContinuousWork(client_id, client_secret, recipients=recipients)
    continuous.run()
