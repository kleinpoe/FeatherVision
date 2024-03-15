from typing import Callable
import tornado
from picamera2.outputs import Output


class StreamOutput(Output):

    def __init__(self, loop:tornado.ioloop.IOLoop, hasConnections:Callable[[],bool], broadcast:Callable):
        super().__init__()
        self.loop = loop
        self.hasConnections = hasConnections
        self.broadcast = broadcast

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        #log(f'Received highres image len{len(frame)} {isKeyframe} {timestamp}')
        if self.loop is not None and self.hasConnections():
            self.loop.add_callback(callback=self.broadcast, frame=frame, timestamp=timestamp, isKeyframe=isKeyframe)