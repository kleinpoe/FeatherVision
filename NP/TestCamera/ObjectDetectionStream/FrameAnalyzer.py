from collections import deque
from dataclasses import dataclass
from datetime import timedelta
from statistics import mean
import subprocess
from typing import Callable, Optional
import cv2
import numpy as np
import tornado

from FrameAnnotator import FrameAnnotator
from StreamOutput import CircularBufferOutput, StreamOutput
from ObjectDetection import Detection, ObjectDetector

from picamera2 import Picamera2

from log import log


class FrameAnalyzer:
    def __init__(self, detector:ObjectDetector, picamera:Picamera2, broadcastDetections: Callable[[list[Detection]],None], getCurentTimestamp: Callable[[],int], circularBuffer: CircularBufferOutput, frameAnnotator: FrameAnnotator):
        self.detector = detector
        self.camera = picamera
        self.broadcastDetections = broadcastDetections
        self.history = DetectionHistory(maxEntries=100000, labelsOfTrackedObjects=["bird"])
        self.getCurentTimestamp = getCurentTimestamp
        self.circularBuffer = circularBuffer
        self.frameAnnotator = frameAnnotator

    def AnalyzeFrames(self):
        log('Started Frame Analyses')
        while True:
            #log(f'Capturing New LoRes-Frame')
            timestamp1 = self.getCurentTimestamp()
            request = self.camera.capture_request()
            frame = request.make_array(name='lores')
            #metadata = request.get_metadata()
            request.release()
            timestamp2 = self.getCurentTimestamp()
            timestamp = int((timestamp1 + timestamp2)/2)
            #log(f'Captured New LoRes-Frame: NumberOfBytes={len(frame)}, Timestamps[{timestamp1}-{timestamp2}] TimeStamp={timestamp}µs')
            
            rgbFrame = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)[:,:854,:]
            
            results = self.detector.Detect(rgbFrame)
            #log([(result.Label,result.Score) for result in results])
            resultsOverThresholdScore = [result for result in results if result.Score > 0.3]
            self.broadcastDetections(resultsOverThresholdScore)
            optionalClip = self.history.CheckClip(rgbFrame, timestamp, resultsOverThresholdScore)
            if optionalClip is not None:
                
                print('New Clip!')
                print(optionalClip[0])
                print(optionalClip[-1])
                
                annotatedFrames = [self.frameAnnotator.AnnotateDetectedObjects(x.Frame,x.Detections) for x in optionalClip]
                height,width,_ = annotatedFrames[0].shape
                clipFps = 1/(mean([f2.Timestamp - f1.Timestamp for f1, f2 in zip(optionalClip, optionalClip[1:])]) / 1E6)

                print(f'Writing annotated Clip: W{width}xH{height} FPS{clipFps} Frames{len(annotatedFrames)} Duration{(optionalClip[-1].Timestamp-optionalClip[0].Timestamp)/1E6:.2f}s')
                codec = cv2.VideoWriter.fourcc(*'mp4v')
                videoWriter = cv2.VideoWriter('testAnnotate.mp4',codec,clipFps,(width,height))
                for frame in annotatedFrames:
                    videoWriter.write(frame)
                videoWriter.release()
                
                richFrames = self.circularBuffer.GetFrames(optionalClip[0].Timestamp, optionalClip[-1].Timestamp)
                
                videoPath = 'test.h264'
                convertedPath = 'test.mp4'
                # Write Circular Buffer to h264 file
                with open(videoPath, "wb") as file:
                    print(f"Writing frames to {videoPath}")
                    size = 0
                    length = len(richFrames)
                    for richFrame in richFrames:
                        file.write(richFrame.Frame)
                        size = size + len(richFrame.Frame)
                    print(f"Done. Length = {size/1E6}Mb. {length/1E6}s")

                # Convert h264 file to mp4
                print("Converting file to mp4")
                command = f"ffmpeg -r {30} -i {videoPath} -y -c copy {convertedPath}"
                subprocess.call(command.split(" "))
    

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
        # It is possible to configure this so it will not work. Durations and maxlen.
        self.maxDurationWithoutTrackedObject = timedelta(seconds=3)
        self.maxClipDuration = timedelta(seconds=60)
        self.minDurationOfTrackedObjectsForClip = timedelta(seconds=3)
        self.clipDurationPaddingStart = timedelta(seconds=1)
        self.clipDurationPaddingEnd = timedelta(seconds=1)
        if self.clipDurationPaddingStart > self.maxDurationWithoutTrackedObject:
            raise ValueError(f"The clip duration start padding {self.clipDurationPaddingStart} must be smaller than the max duration without tracked object {self.maxDurationWithoutTrackedObject}")
        if self.clipDurationPaddingEnd > self.maxDurationWithoutTrackedObject:
            raise ValueError(f"The clip duration end padding {self.clipDurationPaddingEnd} must be smaller than the max duration without tracked object {self.maxDurationWithoutTrackedObject}")
        
        self.history:deque[DetectionHistoryEntry] = deque(maxlen=maxEntries)
        self.EntryWhereTrackedObjectWasDetectedFirst:Optional[DetectionHistoryEntry] = None
        self.EntryWhereTrackedObjectWasDetectedLast:Optional[DetectionHistoryEntry] = None
        
    def CheckClip(self, frame: np.ndarray, timestamp: int, detections: list[Detection]) -> Optional[list[DetectionHistoryEntry]]:
        
        entry = DetectionHistoryEntry(detections, timestamp, frame)
        self.history.append(entry)
        
        hasTrackedObject = any(detection.Label in self.labelsOfTrackedObjects for detection in detections)
        thereIsATrackedObjectInHistory = self.EntryWhereTrackedObjectWasDetectedLast is not None
        timeSinceLastTrackedObjectIsAboveLimit = (entry.Timestamp - self.EntryWhereTrackedObjectWasDetectedLast.Timestamp) > self.maxDurationWithoutTrackedObject.total_seconds() * 1000000 if thereIsATrackedObjectInHistory and not hasTrackedObject else False
        clipExceedsMaxDuration = (entry.Timestamp - self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp) + self.clipDurationPaddingStart.total_seconds() * 1E6 > self.maxClipDuration.total_seconds() * 1000000 if thereIsATrackedObjectInHistory else False
        clipIsLongEnough = (self.EntryWhereTrackedObjectWasDetectedLast.Timestamp - self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp) > self.minDurationOfTrackedObjectsForClip.total_seconds() * 1000000 if thereIsATrackedObjectInHistory else False
        
        match (hasTrackedObject,thereIsATrackedObjectInHistory,timeSinceLastTrackedObjectIsAboveLimit, clipExceedsMaxDuration, clipIsLongEnough):
            case (_, True, _, True, _):
                # The clip became too long already -> output
                #log('The clip became too long already -> output')
                clipBegin = self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp - self.clipDurationPaddingStart.total_seconds() * 1000000
                clipEnd = entry.Timestamp
                self.EntryWhereTrackedObjectWasDetectedFirst = None
                self.EntryWhereTrackedObjectWasDetectedLast = None
                return self.SliceByTime(clipBegin, clipEnd)
            case (False, False, _, _, _):
                # Nothing new detected, also no last tracked object detection
                #log('Nothing new detected, also no last tracked object detection')
                return None
            case (True, False, _, _, _):
                # The first tracked object is detected
                #log('The first tracked object is detected')
                self.EntryWhereTrackedObjectWasDetectedFirst = entry
                self.EntryWhereTrackedObjectWasDetectedLast = entry
                return None
            case (True, True, _, _, _):
                # A tracked object is detected, but not the first
                #log('A tracked object is detected, but not the first')
                self.EntryWhereTrackedObjectWasDetectedLast = entry
                return None
            case (False, True, True, _, True):
                # Nothing new detected and last tracked object detection is long enough ago to return clip and tracked object detection duration is long enough -> output
                #log('Nothing new detected and last tracked object detection is long enough ago to return clip and tracked object detection duration is long enough -> output')
                clipBegin = self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp - self.clipDurationPaddingStart.total_seconds() * 1000000
                clipEnd = self.EntryWhereTrackedObjectWasDetectedLast.Timestamp + self.clipDurationPaddingEnd.total_seconds() * 1000000
                self.EntryWhereTrackedObjectWasDetectedFirst = None
                self.EntryWhereTrackedObjectWasDetectedLast = None
                return self.SliceByTime(clipBegin, clipEnd)
            case (False, True, True, _, False):
                # Nothing new detected and last tracked object detection is long enough ago to return clip but tracked object detection duration is not long enough
                #log('Nothing new detected and last tracked object detection is long enough ago to return clip but tracked object detection duration is not long enough')
                self.EntryWhereTrackedObjectWasDetectedFirst = None
                self.EntryWhereTrackedObjectWasDetectedLast = None
                return None
            case(False, True, False, False, _):
                # Nothing new detected, but last tracked object detection is not long enough ago to return clip
                #log('Nothing new detected, but last tracked object detection is not long enough ago to return clip')
                return None
            case _:
                raise NotImplementedError(f'''A case in the detection history has occured that was not considered. 
                                        hasTrackedObject={hasTrackedObject}, 
                                        thereIsATrackedObjectInHistory={thereIsATrackedObjectInHistory}, 
                                        timeSinceLastTrackedObjectIsAboveLimit={timeSinceLastTrackedObjectIsAboveLimit}, 
                                        clipExceedsMaxDuration={clipExceedsMaxDuration},
                                        clipIsLongEnough={clipIsLongEnough}''')
            
    
    def SliceByTime(self, timestampMin:int, timestampMax:int) -> list[DetectionHistoryEntry]:
        closestToMin = min(self.history, key= lambda entry: abs(entry.Timestamp - timestampMin))
        closestToMax = min(self.history, key= lambda entry: abs(entry.Timestamp - timestampMax))
        minIndex = self.history.index(closestToMin)
        maxIndex = self.history.index(closestToMax)
        return list(self.history)[minIndex:maxIndex]
        
        
    