from logging import Logger
from urllib.request import urlopen
import time

class NetworkChecker:
    
    def __init__(self, logger:Logger):
        self.myLogger = logger

    def InternetAvailable(self, host='http://google.com'):
        try:
            urlopen(host)
            return True
        except Exception as e:
            return False

    def WaitTillInternetAvailable(self):
        while not self.InternetAvailable():
            time.sleep(1)
        self.myLogger.info('InternetConnectionChecker: Connected to Internet.')
