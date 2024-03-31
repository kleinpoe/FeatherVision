from Infrastructure.Clock import Clock
from Config.Config import Config
from ClipDatabase.ClipDatabase import ClipDatabase

import tornado.web

from logging import Logger


class RequestHandlerBase(tornado.web.RequestHandler):

    @property
    def config(self) -> Config:
        return self.application.settings.get('config')

    @property
    def logger(self) -> Logger:
        return self.application.settings.get('logger')
    
    @property
    def clipDatabase(self) -> ClipDatabase:
        return self.application.settings.get('clipDatabase')
    
    @property
    def clock(self) -> Clock:
        return self.application.settings.get('clock')