import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

from Config.Config import Config

class LoggerFactory:

    def __init__(self, config:Config):
        self.myConfig = config

    def CreateLogger(self) -> Logger:
        config = self.myConfig
        handlers = []
        if config.LoggingConfig.LogToFile:
            handlers.append(RotatingFileHandler(config.StorageConfig.LogFilePath, 
                                                maxBytes=config.LoggingConfig.MaximumLogBytes, 
                                                backupCount=config.LoggingConfig.LogBackupFiles))
        handlers.append(logging.StreamHandler())

        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(module)-35s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.WARN, handlers=handlers)
        logging.captureWarnings(True)
        LoggerName: str = "ApplicationLogger"
        ApplicationLogger = logging.getLogger(LoggerName)
        ApplicationLogger.setLevel(config.LoggingConfig.LogLevel)