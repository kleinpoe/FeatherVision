from threading import Lock
from Camera.Frames.HighResolutionFrame import HighResolutionFrame
from Config.Config import Config
from Surveillance.ObjectDetection.Detection import Detection
from WebInterface.Handlers.StreamingHandler import StreamingHandler


import tornado
import tornado.websocket


import struct
from logging import Logger


class StreamingHandlerManager:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.connections:list[StreamingHandler] = []
        self.detections: list[Detection] = []
        self.lock = Lock()

    def Register(self, streamingHandler: StreamingHandler):
        self.logger.info(f'A new Streaming Connection from IP="{streamingHandler.request.remote_ip}" was established.')
        self.connections.append(streamingHandler)

    def Unregister(self, streamingHandler: StreamingHandler):
        self.logger.info(f'Streaming Connection from IP="{streamingHandler.request.remote_ip}" was closed.')
        self.connections.remove(streamingHandler)

    def HasConnections(self):
        return len(self.connections) > 0

    def UpdateDetections(self, detections: list[Detection]):
        with self.lock:
            self.detections = detections

    async def Broadcast(self, frame:HighResolutionFrame):
        for connection in self.connections:
            try:
                if connection.LastFrameTimestampReceivedByClient == connection.LastSentFrameTimestamp:
                    
                    with self.lock:
                        detections = self.detections
                    
                    # Todo extract to class
                    #[detectionCount 4-bytes][Top:4bytes,Left:4bytes,Bottom:4bytes,Right:4bytes,Score:4bytes,Label:8bytes]...[isKeyFrame:1byte][timestamp:8bytes][frame:Xbytes(to end)]
                    endianness='little'
                    detectionsInBytes=b''.join(
                    [struct.pack('f',d.BoundingBox.Top)
                     + struct.pack('f',d.BoundingBox.Left)
                     + struct.pack('f',d.BoundingBox.Bottom)
                     + struct.pack('f',d.BoundingBox.Right)
                     + struct.pack('f',d.Score)
                     + f"{d.Label[:12]:<12}".encode('utf-8')  for d in detections])
                    detectionLengthInBytes=len(detections).to_bytes(4,endianness)

                    isKeyframeInBytes = frame.IsKeyframe.to_bytes(1,endianness)
                    # To do send identifier, refactor data transmission
                    timestampInBytes = frame.RawTimestamp.to_bytes(8, endianness)

                    payload = detectionLengthInBytes + detectionsInBytes + isKeyframeInBytes + timestampInBytes + frame.Frame
                    #log(f"Sending frame timestamp=<{timestamp}> keyframe=<{isKeyframe}> Detections={[x for x in cl.detections]}")
                    await connection.write_message(payload, True)
                    connection.LastSentFrameTimestamp = frame.RawTimestamp
                else:
                    # To Do refactor warning spam
                    self.logger.warn(f'Skipping frame timestamp=<{frame.RawTimestamp}> due to bad connection. Total skip = {(frame.RawTimestamp - connection.LastFrameTimestampReceivedByClient)/1E3}ms')
            except tornado.websocket.WebSocketClosedError:
                pass
            except tornado.iostream.StreamClosedError:
                pass