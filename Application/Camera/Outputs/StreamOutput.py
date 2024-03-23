from datetime import datetime, timedelta
from typing import Callable
from picamera2.outputs import Output
from Camera.Frames.HighResolutionFrame import HighResolutionFrame

class StreamOutput(Output):
    def __init__(self, referenceTimestamp:datetime, broadcast:Callable[[HighResolutionFrame],None]):
        self.broadcast = broadcast
        self.referenceTimestamp = referenceTimestamp

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int) -> None:
        timestamp = self.referenceTimestamp + timedelta( microseconds= timestamp)
        self.broadcast(HighResolutionFrame(frame,isKeyframe,timestamp))
        
        