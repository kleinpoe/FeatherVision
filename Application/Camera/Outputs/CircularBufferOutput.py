from datetime import datetime, timedelta
from Application.Camera.Frames.HighResolutionFrame import HighResolutionFrame

from picamera2.outputs import Output

from collections import deque
from threading import Lock


class CircularBufferOutput(Output):
    def __init__(self, numberOfFrames:int, referenceTimestamp: datetime):
        super().__init__()
        self.buffer:deque[HighResolutionFrame] = deque(maxlen=numberOfFrames)
        self.referenceTimestamp = referenceTimestamp
        self.bufferLock = Lock()

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        timestamp = self.referenceTimestamp + timedelta( microseconds= timestamp)
        frame = HighResolutionFrame(frame,isKeyframe,timestamp)
        with self.bufferLock:
            self.buffer.append(frame)

    def GetFrames(self, timestampMin:datetime, timestampMax:datetime) -> list[HighResolutionFrame]:
        shallowCopiedBuffer = []
        with self.bufferLock:
            shallowCopiedBuffer = [x for x in self.buffer]
        # Consider Performance Optimizations
        keyFrames = [frame for frame in shallowCopiedBuffer if frame.IsKeyframe]
        closestKeyFrameToMin = min(keyFrames, key= lambda frame: abs(frame.Timestamp - timestampMin))
        closestFrameToMax = min(shallowCopiedBuffer, key= lambda frame: abs(frame.Timestamp - timestampMax))
        return shallowCopiedBuffer[shallowCopiedBuffer.index(closestKeyFrameToMin):shallowCopiedBuffer.index(closestFrameToMax)]