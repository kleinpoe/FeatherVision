import struct
import tornado.web, tornado.ioloop, tornado.websocket  
import os, socket


from FrameAnalyzer import FrameAnalyzer
from StreamOutput import CircularBufferOutput, MultiOutput, RichFrame, StreamOutput, SynchronizationOutput
from log import log

import threading

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

from ObjectDetection import Detection, ImagePreparation, ObjectDetector

from PerformanceMonitor import PerformanceMonitor



abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# config
serverPort = 8000
mainResolution = (1920,1080)
detectionResolution = (854,480)
fps = 30
circularBufferSeconds = 100

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

def getBroadcastFunc(loop:tornado.ioloop.IOLoop):
    def broadcastFunc(richFrame:RichFrame):
        if loop is not None and wsHandler.hasConnections():
            loop.add_callback(callback=wsHandler.broadcast, frame=richFrame.Frame, timestamp=richFrame.Timestamp, isKeyframe=richFrame.IsKeyframe)
    return broadcastFunc

def getBroadcastDetectionsFunc(loop:tornado.ioloop.IOLoop):
    def broadcastFunc(detections:list[Detection]):
        if loop is not None and wsHandler.hasConnections():
            loop.add_callback(callback=wsHandler.updateDetections, detections=detections)
    return broadcastFunc

try:
    detector = ObjectDetector(detectionModelFile,detectionModelLabelsFile, ImagePreparation())
    performanceMonitor = PerformanceMonitor(2)
    performanceMonitor.Start()
    application = tornado.web.Application(requestHandlers,**settings)
    application.listen(serverPort)
    loop = tornado.ioloop.IOLoop.current()
    
    streamOutput = StreamOutput(getBroadcastFunc(loop))
    circularOutput = CircularBufferOutput(numberOfFrames=circularBufferSeconds*fps)
    synchronizationOutput = SynchronizationOutput()
    mainOutput = MultiOutput([synchronizationOutput,circularOutput,streamOutput])
    
    analyzer = FrameAnalyzer(detector,picam2, getBroadcastDetectionsFunc(loop), synchronizationOutput.GetCurrentTimestamp, circularOutput)
    picam2.start_recording(mainEncoder, mainOutput)
    threading.Thread(target=analyzer.AnalyzeFrames, daemon=True).start()
    loop.start()
finally:
    picam2.stop_recording()
    picam2.close()
    loop.stop()