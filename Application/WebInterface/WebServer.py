from logging import Logger
import tornado.web, tornado.ioloop, tornado.websocket

from WebInterface.StreamingHandlerManager import StreamingHandlerManager
from WebInterface.MainHandler import MainHandler
from WebInterface.StreamingHandler import StreamingHandler
from Config.Config import Config  

class WebServer:
    
    def __init__(self, streamingHandlerManager: StreamingHandlerManager, config: Config, logger: Logger):
        self.streamingHandlerManager = streamingHandlerManager
        self.config = config
        self.logger = logger
        self.loop = tornado.ioloop.IOLoop.current()
        
        
    def Start(self):
        self.logger.info(f"Starting Web Server. Connect to it using {self.config.WebInterface.Ip}:{self.config.WebInterface.Port}")
        
        settings = {"static_path": self.config.WebInterface.Content.StaticDirectory,
                    "config": self.config,
                    "logger": self.logger,
                    "registerFunc": self.streamingHandlerManager.Register,
                    "unregisterFunc": self.streamingHandlerManager.Unregister}

        requestHandlers = [(r"/ws/", StreamingHandler),
            (r"/", MainHandler),
            (r"/index.html", MainHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, 
             dict(path=settings['static_path']))]
        
        self.application = tornado.web.Application(requestHandlers,**settings)
        self.application.listen(self.config.WebInterface.Port)
        self.loop.start()
    
    def Stop(self):
        self.logger.info(f"Shutting down Web Server.")
        self.loop.stop()