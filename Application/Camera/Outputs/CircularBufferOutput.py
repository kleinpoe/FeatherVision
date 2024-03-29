from datetime import datetime, timedelta
from collections import deque
from threading import Lock
from picamera2.outputs import Output

from Config.Config import Config
from Camera.Frames.HighResolutionFrame import HighResolutionFrame


class CircularBufferOutput(Output):
    def __init__(self, referenceTimestamp: datetime, config: Config):
        super().__init__()
        frameCapacity = int(config.Camera.Fps * config.ClipGeneration.HighResolutionFrameBufferDuration.total_seconds())
        self.buffer:deque[HighResolutionFrame] = deque(maxlen=frameCapacity)
        self.referenceTimestamp = referenceTimestamp
        self.bufferLock = Lock()

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        timestampAsDatetime = self.referenceTimestamp + timedelta( microseconds= timestamp)
        frame = HighResolutionFrame(frame,isKeyframe,timestampAsDatetime,timestamp)
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