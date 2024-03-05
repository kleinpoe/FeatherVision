import tornado.web, tornado.ioloop, tornado.websocket  
from string import Template
import io, os, socket

from datetime import timedelta
import time

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput

from CustomOutput import CustomOutput

import subprocess

from collections import deque
from picamera2.outputs import Output

# start configuration
serverPort = 8000

# setup camera
picam2 = Picamera2()
fps = 30
recordingDuration = timedelta(seconds=10)
videoConfig = picam2.create_video_configuration(main={"size":(1920,1080)},
                                            controls={'FrameRate':fps})
picam2.configure(videoConfig)
encoder = H264Encoder(framerate=fps)
output = CustomOutput()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))
serverIp = s.getsockname()[0]

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def getFile(filePath):
    file = open(filePath,'r')
    content = file.read()
    file.close()
    return content

def templatize(content, replacements):
    tmpl = Template(content)
    return tmpl.substitute(replacements)

indexHtml = templatize(getFile('index.html'), {'ip':serverIp, 'port':serverPort, 'fps':fps})
jmuxerJs = getFile('jmuxer.min.js')

class StreamOutput(Output):

    def __init__(self):
        super().__init__()

    def outputframe(self, frame, keyframe, timestamp):
        if self.loop is not None and wsHandler.hasConnections():
            self.loop.add_callback(callback=wsHandler.broadcast, message=frame)

    def start(self):
        super().start()

    def stop(self):
        super().stop()

    def setLoop(self, loop):
        self.loop = loop

class wsHandler(tornado.websocket.WebSocketHandler):
    connections = []

    def open(self):
        self.connections.append(self)

    def on_close(self):
        self.connections.remove(self)

    def on_message(self, message):
        pass

    @classmethod
    def hasConnections(cl):
        if len(cl.connections) == 0:
            return False
        return True

    @classmethod
    async def broadcast(cl, message):
        for connection in cl.connections:
            try:
                await connection.write_message(message, True)
            except tornado.websocket.WebSocketClosedError:
                pass
            except tornado.iostream.StreamClosedError:
                pass

    def check_origin(self, origin):
        return True

class indexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(indexHtml)

class jmuxerHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/javascript')
        self.write(jmuxerJs)

requestHandlers = [
    (r"/ws/", wsHandler),
    (r"/", indexHandler),
    (r"/index.html", indexHandler),
    (r"/jmuxer.min.js", jmuxerHandler)
]

try:
    output = StreamOutput()
    application = tornado.web.Application(requestHandlers)
    application.listen(serverPort)
    loop = tornado.ioloop.IOLoop.current()
    output.setLoop(loop)
    picam2.start_recording(encoder, output)
    output.start()
    loop.start()
except KeyboardInterrupt:
    picam2.stop_recording()
    output.stop()
    picam2.close()
    loop.stop()