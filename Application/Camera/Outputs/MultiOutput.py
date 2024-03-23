from picamera2.outputs import Output


class MultiOutput(Output):
    def __init__(self, outputs:list[Output]):
        self.outputs = outputs

    def outputframe(self, frame: bytes, isKeyframe: bool, timestamp: int):
        #log(f'New HighRes-Frame: NumberOfBytes={len(frame)}, KeyFrame={isKeyframe}, TimeStamp={timestamp}µs')
        for output in self.outputs:
            output.outputframe(frame, isKeyframe, timestamp)