from logging import Logger
import tornado.web, tornado.ioloop, tornado.websocket

from Application.WebInterface.MainHandler import MainHandler
from Application.WebInterface.StreamingHandler import StreamingHandler
from Config.Config import Config  

class WebServer:
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.loop = tornado.ioloop.IOLoop.current()
        
        
    def Start(self):
        self.logger.info("Starting Web Server")
        
        settings = {"static_path": self.config.WebInterface.HtmlStaticDirectory,
                    "config": self.config,
                    "logger": self.logger}

        requestHandlers = [(r"/ws/", StreamingHandler),
            (r"/", MainHandler),
            (r"/index.html", MainHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))]
        
        self.application = tornado.web.Application(requestHandlers,**settings)
        self.application.listen(self.config.WebInterface.Port)
        self.loop.start()
    
    def Stop(self):
        self.loop.stop()