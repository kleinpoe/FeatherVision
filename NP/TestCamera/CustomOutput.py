
from collections import deque
from picamera2.outputs import Output

class CustomOutput(Output):

    def __init__(self):
        super().__init__()
        self.Buffer = deque()

    def outputframe(self, frame, keyframe, timestamp):
        temp = self.GetCpuTemperature()
        print(f"Received Frame Bytes={len(frame)} KeyFrame={keyframe} TimeStamp={timestamp} T={temp}°C")
        if(len(self.Buffer) > 0 or keyframe):
            self.Buffer.append((frame, timestamp))

    def start(self):
        super().start()

    def stop(self):
        super().stop()
        
    def GetCpuTemperature(self):
        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        raw = f.read().rstrip()
        result = float(raw[:-3] + "." + raw[-3:])
        f.close()
        return result