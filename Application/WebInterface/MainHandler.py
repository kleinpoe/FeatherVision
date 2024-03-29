from logging import Logger
from Config.Config import Config

import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):

    def getConfig(self) -> Config:
        return self.application.settings.get('config')
    
    def getLogger(self) -> Logger:
        return self.application.settings.get('logger')

    def get(self):
        config = self.getConfig()
        path = os.path.join(config.WebInterface.Content.IndexHtml)
        self.render(path,fps=config.Camera.Fps,ip=config.WebInterface.Ip,port=config.WebInterface.Port)