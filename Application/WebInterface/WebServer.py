import asyncio
from logging import Logger
from typing import Callable
import tornado.web, tornado.ioloop, tornado.websocket

from Infrastructure.Clock import Clock
from ClipDatabase.ClipDatabase import ClipDatabase
from WebInterface.StreamingHandlerManager import StreamingHandlerManager
from WebInterface.Handlers.MainHandler import BrowseVideoHandler, MainHandler, WatchVideoHandler
from WebInterface.Handlers.StreamingHandler import StreamingHandler
from Config.Config import Config  

class WebServer:
    
    def __init__(self, streamingHandlerManager: StreamingHandlerManager, clipDatabase:ClipDatabase, clock:Clock, config: Config, logger: Logger):
        self.streamingHandlerManager = streamingHandlerManager
        self.clipDatabase = clipDatabase
        self.config = config
        self.logger = logger
        self.clock = clock
        self.loop = tornado.ioloop.IOLoop.current()
        
    def GetCallback(self, function: Callable) -> Callable:
        def callback(**kwargs):
            self.loop.add_callback(callback=function, **kwargs)
        return callback
        
        
    def Start(self):
        self.logger.info(f"Starting Web Server. Connect to it using {self.config.WebInterface.Ip}:{self.config.WebInterface.Port}")
        
        settings = {"static_path": self.config.WebInterface.Content.StaticDirectory,
                    "config": self.config,
                    "logger": self.logger,
                    "registerFunc": self.streamingHandlerManager.Register,
                    "unregisterFunc": self.streamingHandlerManager.Unregister,
                    "clipDatabase": self.clipDatabase,
                    "clock": self.clock}

        requestHandlers = [(r"/ws/", StreamingHandler),
            (r"/", MainHandler),
            (r"/index.html", MainHandler),
            (r"/watch/(.+)", WatchVideoHandler),
            (r"/browse/(.+)", BrowseVideoHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))]
        
        self.application = tornado.web.Application(requestHandlers,**settings)
        self.application.listen(self.config.WebInterface.Port)
        self.loop.start()
    
    def Stop(self):
        self.logger.info(f"Shutting down Web Server.")
        self.loop.stop()