from dataclasses import dataclass
from typing import Optional
from ObjectDetection import Detection
from log import log


import numpy as np

from collections import deque
from datetime import timedelta


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
                log('The first tracked object is detected')
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