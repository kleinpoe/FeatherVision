from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Callable
from picamera2.outputs import Output

@dataclass
class RichFrame:
    Frame:bytes
    IsKeyframe:bool
    Timestamp:int

class MultiOutput(Output):
    def __init__(self, outputs:list[Output]):
        self.outputs = outputs

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        #log(f'Received Frame data: Number of Bytes={len(frame)}, KeyFrame={isKeyframe}, TimeStamp={timestamp}µs')
        for output in self.outputs:
            output.outputframe(frame, isKeyframe, timestamp)

class StreamOutput(Output):
    def __init__(self, broadcast:Callable[[RichFrame],None]):
        self.broadcast = broadcast

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        self.broadcast(RichFrame(frame,isKeyframe,timestamp))
        
class SynchronizationOutput(Output):
    def __init__(self):
        self.currentTimestamp:int = 0
        self.lock = Lock()

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        with self.lock:
            self.currentTimestamp = timestamp
        
    def GetCurrentTimestamp(self)->int:
        with self.lock:
            return self.currentTimestamp
            
        
class CircularBufferOutput(Output):
    def __init__(self, numberOfFrames:int):
        super().__init__()
        self.buffer:deque[RichFrame] = deque(maxlen=numberOfFrames)
        self.bufferLock = Lock()

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        richFrame = RichFrame(frame,isKeyframe,timestamp)
        with self.bufferLock:
            self.buffer.append(richFrame)
            
    def GetFrames(self, timestampMin:int, timestampMax:int) -> list[RichFrame]:
        shallowCopiedBuffer = []
        with self.bufferLock:
            shallowCopiedBuffer = [x for x in self.buffer]
        # Consider Performance Optimizations
        keyFrames = [frame for frame in shallowCopiedBuffer if frame.IsKeyframe]
        closestKeyFrameToMin = min(keyFrames, key= lambda frame: abs(frame.Timestamp - timestampMin))
        closestKeyFrameToMax = min(shallowCopiedBuffer, key= lambda frame: abs(frame.Timestamp - timestampMax))
        return shallowCopiedBuffer[shallowCopiedBuffer.index(closestKeyFrameToMin):shallowCopiedBuffer.index(closestKeyFrameToMax)]
        