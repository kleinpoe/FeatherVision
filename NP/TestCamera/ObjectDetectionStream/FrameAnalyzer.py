from collections import deque
from dataclasses import dataclass
from datetime import timedelta
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
            resultsOverThresholdScore = [result for result in results if result.Score > 0.3]
            self.loop.add_callback(callback=self.updateDetectionsCallback, detections=resultsOverThresholdScore)
            self.history.append(results)
    

@dataclass
class RichDetection:
    Detection: Detection
    Timestamp: int

@dataclass
class DetectionHistoryEntry:
    RichDetection: RichDetection
    TimeDifferenceToPrevious: int       
            
class DetectionHistory:
    def __init__(self, maxEntries:int, labelsOfTrackedObjects: list[str]):
        self.labelsOfTrackedObjects = labelsOfTrackedObjects
        self.history:deque[DetectionHistoryEntry] = deque(maxlen=maxEntries)
        self.maxDurationWithoutTrackedObject = timedelta(seconds=3)
        self.maxClipDuration = timedelta(seconds=60)
        
    def Add(self, detections:list[Detection]) -> None:
        for d in detections:
            if self.isTrackingWorthy(d.Label):
                self.history.append(d)
                
    def isTrackingWorthy(self, detection:Detection):
        return detection.Label in self.labelsOfTrackedObjects
                
    def Clear(self) -> None:
        self.history.clear()
        
    def GetClipInterval(self) -> list[Detection]:
        
        
    