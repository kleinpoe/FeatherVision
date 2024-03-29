import tornado
import tornado.websocket
from logging import Logger

from Config.Config import Config

class StreamingHandler(tornado.websocket.WebSocketHandler):

    LastSentFrameTimestamp = -1
    LastFrameTimestampReceivedByClient = -1

    def getConfig(self) -> Config:
        return self.application.settings.get('config')
    
    def getLogger(self) -> Logger:
        return self.application.settings.get('logger')

    def open(self):
        self.application.settings.get('registerFunc')(self)

    def on_close(self):
        self.application.settings.get('unregisterFunc')(self)

    def on_message(self, message):
        timestamp = int.from_bytes(message,'little')
        self.LastFrameTimestampReceivedByClient = timestamp
        #log(f"Response from client. Received frame {timestamp}")

    def check_origin(self, origin):
        return True
    

    
    
