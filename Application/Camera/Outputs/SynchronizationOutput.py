from datetime import timedelta, datetime

from picamera2.outputs import Output

from threading import Lock

class SynchronizationOutput(Output):
    def __init__(self, referenceTimestamp:datetime):
        self.referenceTimestamp = referenceTimestamp
        self.currentTimestamp:datetime = referenceTimestamp
        self.lock = Lock()

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        with self.lock:
            self.currentTimestamp = self.referenceTimestamp + timedelta(microseconds=timestamp)

    def GetCurrentTimestamp(self)->datetime:
        with self.lock:
            return self.currentTimestamp