from logging import Logger
import struct
from Config.Config import Config
from Surveillance.ObjectDetection.Detection import Detection


import tornado
import tornado.websocket


class StreamingHandler(tornado.websocket.WebSocketHandler):


    def getConfig(self) -> Config:
        return self.application.settings.get('config')
    
    def getLogger(self) -> Logger:
        return self.application.settings.get('logger')

    connections:list['StreamingHandler'] = []
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