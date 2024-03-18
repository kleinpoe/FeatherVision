from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Optional
import numpy as np
import tornado

from ObjectDetection import Detection, ObjectDetector

from picamera2 import Picamera2

from log import log


class FrameAnalyzer:
    def __init__(self, detector:ObjectDetector, picamera:Picamera2, broadcastDetections: Callable[[list[Detection]],None], getCurentTimestamp: Callable[[],int]):
        self.detector = detector
        self.camera = picamera
        self.broadcastDetections = broadcastDetections
        self.history = DetectionHistory(maxEntries=100000, labelsOfTrackedObjects=["bird"])
        self.getCurentTimestamp = getCurentTimestamp

    def AnalyzeFrames(self):
        log('Started Frame Analyses')
        while True:
            timestamp1 = self.getCurentTimestamp()
            request = self.camera.capture_request()
            frame = request.make_array(name='lores')
            #metadata = request.get_metadata()
            request.release()
            timestamp2 = self.getCurentTimestamp()
            timestamp = int((timestamp1 + timestamp2)/2)
            
            results = self.detector.Detect(frame)
            #log([(result.Label,result.Score) for result in results])
            resultsOverThresholdScore = [result for result in results if result.Score > 0.3]
            self.broadcastDetections(resultsOverThresholdScore)
            optionalClip = self.history.CheckClip(DetectionHistoryEntry(resultsOverThresholdScore, timestamp, frame ))
            if optionalClip is not None:
                print('New Clip!')
                print(optionalClip[0])
                print(optionalClip[-1])
    

@dataclass
class DetectionHistoryEntry:
    Detections: list[Detection]
    Timestamp: int
    Frame: np.ndarray
    
    def __repr__(self) -> str:
        formattedDetections = ' '.join([f'{x.Label}({x.Score*100:.0f}%)' for x in self.Detections])
        return f'<Entry {self.Timestamp} Detections=[ {formattedDetections} ]>'
            
class DetectionHistory:
    def __init__(self, maxEntries:int, labelsOfTrackedObjects: list[str]):
        self.labelsOfTrackedObjects = labelsOfTrackedObjects
        self.history:deque[DetectionHistoryEntry] = deque(maxlen=maxEntries)
        self.maxDurationWithoutTrackedObject = timedelta(seconds=3)
        self.maxClipDuration = timedelta(seconds=60)
        self.minClipDuration = timedelta(seconds=3)
        
    def CheckClip(self, entry:DetectionHistoryEntry) -> Optional[list[DetectionHistoryEntry]]:
        
        # It was too long since last detection, output history
        newTimestamp = entry.Timestamp
        timeSinceLastDetection = 0
        if len(self.history) > 0:
            timeSinceLastDetection = newTimestamp - self.history[-1].Timestamp
            lastDetectionWasTooLongAgoToKeepWaiting = timeSinceLastDetection > self.maxDurationWithoutTrackedObject.total_seconds() * 1E6
            historyLength = self.history[-1].Timestamp - self.history[0].Timestamp
            lastDetectionsWereLongEnough = historyLength > self.minClipDuration.total_seconds() * 1E6
            if lastDetectionWasTooLongAgoToKeepWaiting and lastDetectionsWereLongEnough:
                print(f'New clip: newTimestamp{newTimestamp} timeSinceLastDetection{timeSinceLastDetection} lastDetectionWasTooLongAgoToKeepWaiting{lastDetectionWasTooLongAgoToKeepWaiting} historyLength{historyLength} lastDetectionsWereLongEnough{lastDetectionsWereLongEnough}')
                output = [x for x in self.history]
                self.history.clear()
                return output
            if lastDetectionWasTooLongAgoToKeepWaiting and not lastDetectionsWereLongEnough:
                print(f'No new clip: newTimestamp{newTimestamp} timeSinceLastDetection{timeSinceLastDetection} lastDetectionWasTooLongAgoToKeepWaiting{lastDetectionWasTooLongAgoToKeepWaiting} historyLength{historyLength} lastDetectionsWereLongEnough{lastDetectionsWereLongEnough}')
                self.history.clear()
        
        # Add new detection if it contains worthy objects
        for detection in entry.Detections:
            if detection.Label in self.labelsOfTrackedObjects:
                self.history.append(entry)
        
        # Clip is too long, output history
        # BUG: this is not very accurate, the max duration will vary but okay for now
        if len(self.history) > 0:        
            historyLength = self.history[-1].Timestamp - self.history[0].Timestamp
            if historyLength > self.maxClipDuration.total_seconds() * 1E6:
                output = [x for x in self.history]
                self.history.clear()
                return output
        
        
    