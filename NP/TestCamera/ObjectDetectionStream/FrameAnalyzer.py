from typing import Callable
import tornado

from ObjectDetection import Detection, ObjectDetector

from picamera2 import Picamera2

from log import log


class FrameAnalyzer:
    def __init__(self, detector:ObjectDetector, loop:tornado.ioloop.IOLoop, picamera:Picamera2, updateDetectionsCallback: Callable):
        self.detector = detector
        self.camera = picamera
        self.loop = loop
        self.updateDetectionsCallback = updateDetectionsCallback
        self.history:list[Detection] = []

    def AnalyzeFrames(self):
        log('Started Frame Analyses')
        while True:
            frame = self.camera.capture_array(name='lores')
            results = self.detector.Detect(frame)
            #log([(result.Label,result.Score) for result in results])
            results = [result for result in results if result.Score > 0.3]
            self.loop.add_callback(callback=self.updateDetectionsCallback, detections=results)
            self.history.append(results)