import struct
import tornado.web, tornado.ioloop, tornado.websocket  
from string import Template
import io, os, socket

from datetime import timedelta
import time

import threading

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, JpegEncoder, MJPEGEncoder

import subprocess
import logging

from collections import deque
from picamera2.outputs import Output
from datetime import datetime
from ObjectDetection import Detection, ObjectDetection

import numpy as np

from PerformanceMonitor import PerformanceMonitor

def log(message):
    timestamp = datetime.utcnow().strftime("%H:%M:%S.%f")
    print(f"[{timestamp}] {message}")

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# config
serverPort = 8000
mainResolution = (1920,1080)
detectionResolution = (854,480)
fps = 30

detectionModelFile = "TfLiteModels/mobilenet_v2.tflite"
detectionModelLabelsFile = "TfLiteModels/coco_labels.txt"

# Setup Camera
picam2 = Picamera2()
videoConfig = picam2.create_video_configuration(main={"size":mainResolution},
                                                lores={"size":detectionResolution},
                                                controls={'FrameRate':fps})
picam2.configure(videoConfig)
mainEncoder= H264Encoder(framerate=fps)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))
serverIp = s.getsockname()[0]
log(f'Connect to server \"{serverIp}:{serverPort}\"')

detection = ObjectDetection(detectionModelFile,detectionModelLabelsFile)


class StreamOutput(Output):

    def __init__(self, loop:tornado.ioloop.IOLoop):
        super().__init__()
        self.loop = loop

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        #log(f'Received highres image len{len(frame)} {isKeyframe} {timestamp}')
        if self.loop is not None and wsHandler.hasConnections():
            self.loop.add_callback(callback=wsHandler.broadcast, frame=frame, timestamp=timestamp, isKeyframe=isKeyframe)

class wsHandler(tornado.websocket.WebSocketHandler):
    connections:list['wsHandler'] = []
    detections: list[Detection] = []
    
    LastSentFrameTimestamp = -1
    LastFrameTimestampReceivedByClient = -1

    def open(self):
        print(f"New connection! {self}")
        self.connections.append(self)

    def on_close(self):
        print("Closed connection!")
        self.connections.remove(self)

    def on_message(self, message):
        timestamp = int.from_bytes(message,'little')
        self.LastFrameTimestampReceivedByClient = timestamp
        #log(f"Response from client. Received frame {timestamp}")

    @classmethod
    def hasConnections(cl):
        if len(cl.connections) == 0:
            return False
        return True

    @classmethod
    def updateDetections(cl, detections: list[Detection]):
        cl.detections = detections

    @classmethod
    async def broadcast(cl, frame:bytes, timestamp:int, isKeyframe:bool):
        for connection in cl.connections:
            try:
                if connection.LastFrameTimestampReceivedByClient == connection.LastSentFrameTimestamp:
                    #[detectionCount 4-bytes][Top:4bytes,Left:4bytes,Bottom:4bytes,Right:4bytes,Score:4bytes,Label:8bytes]...[isKeyFrame:1byte][timestamp:8bytes][frame:Xbytes(to end)]
                    endianness='little'
                    
                    detectionsInBytes=b''.join(
                    [struct.pack('f',d.BoundingBox.Top) 
                     + struct.pack('f',d.BoundingBox.Left) 
                     + struct.pack('f',d.BoundingBox.Bottom) 
                     + struct.pack('f',d.BoundingBox.Right) 
                     + struct.pack('f',d.Score) 
                     + f"{d.Label[:12]:<12}".encode('utf-8')  for d in cl.detections])
                    detectionLengthInBytes=len(cl.detections).to_bytes(4,endianness)
    
                    isKeyframeInBytes = isKeyframe.to_bytes(1,endianness)
                    timestampInBytes = timestamp.to_bytes(8, endianness)
                    
                    payload = detectionLengthInBytes + detectionsInBytes + isKeyframeInBytes + timestampInBytes + frame
                    #log(f"Sending frame timestamp=<{timestamp}> keyframe=<{isKeyframe}> Detections={[x for x in cl.detections]}")
                    await connection.write_message(payload, True)
                    connection.LastSentFrameTimestamp = timestamp
                else:
                    log(f'Skipping frame timestamp=<{timestamp}> due to bad connection. Total skip = {(timestamp - connection.LastFrameTimestampReceivedByClient)/1E3}ms')
            except tornado.websocket.WebSocketClosedError:
                pass
            except tornado.iostream.StreamClosedError:
                pass

    def check_origin(self, origin):
        return True

class indexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('WebContent/index.html',fps=fps,ip=serverIp,port=serverPort)

settings = {"static_path": os.path.join(os.path.dirname(__file__), "WebContent", "static"),}

requestHandlers = [
    (r"/ws/", wsHandler),
    (r"/", indexHandler),
    (r"/index.html", indexHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path']))
]

class FrameAnalyzer:
    def __init__(self, loop:tornado.ioloop.IOLoop):
        self.loop = loop

    def AnalyzeFrames(self):
        log('Started Frame Analyses')
        while True:
            frame = picam2.capture_array(name='lores')
            results = detection.Detect(frame)
            #log([(result.Label,result.Score) for result in results])
            results = [result for result in results if result.Score > 0.5]
            self.loop.add_callback(callback=wsHandler.updateDetections, detections=results)

try:
    performanceMonitor = PerformanceMonitor(2)
    performanceMonitor.Start()
    application = tornado.web.Application(requestHandlers,**settings)
    application.listen(serverPort)
    loop = tornado.ioloop.IOLoop.current()
    mainOutput = StreamOutput(loop)
    analyzer = FrameAnalyzer(loop)
    picam2.start_recording(mainEncoder, mainOutput)
    threading.Thread(target=analyzer.AnalyzeFrames, daemon=True).start()
    loop.start()
except KeyboardInterrupt:
    picam2.stop_recording()
    picam2.close()
    loop.stop()