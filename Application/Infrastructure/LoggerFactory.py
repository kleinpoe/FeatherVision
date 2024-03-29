import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

from Config.Config import Config

class LoggerFactory:

    def __init__(self, config:Config):
        self.config = config

    def CreateLogger(self) -> Logger:
        handlers = []
        if self.config.Logging.LogToFile:
            handlers.append(RotatingFileHandler(self.config.Storage.LogFilePath, 
                                                maxBytes=self.config.Logging.MaximumLogBytes, 
                                                backupCount=self.config.Logging.LogBackupFiles))
        handlers.append(logging.StreamHandler())

        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(module)-35s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.WARN, handlers=handlers)
        logging.captureWarnings(True)
        LoggerName: str = "ApplicationLogger"
        ApplicationLogger = logging.getLogger(LoggerName)
        ApplicationLogger.setLevel(self.config.Logging.LogLevel)
        
        return ApplicationLogger