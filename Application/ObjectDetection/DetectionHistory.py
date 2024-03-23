from typing import Optional
from Config.Config import Config
from ObjectDetection.DetectionHistoryEntry import DetectionHistoryEntry
from ObjectDetection import Detection

import numpy as np

from collections import deque
from logging import Logger


class DetectionHistory:
    def __init__(self, config:Config, logger:Logger):
        
        self.config = config.ClipGeneration
        self.logger = logger
        
        if self.config.PaddingStart > self.config.AllowedTrackedObjectGapsDuration or self.config.PaddingEnd > self.config.AllowedTrackedObjectGapsDuration:
            raise ValueError(f"The clip paddings (begin:{self.config.PaddingStart},end:{self.config.PaddingEnd}) must be smaller than the maximum gap duration without tracked object {self.config.AllowedTrackedObjectGapsDuration}")

        self.history:deque[DetectionHistoryEntry] = deque(maxlen=self.config.DetectionHistoryMaxEntries)
        self.EntryWhereTrackedObjectWasDetectedFirst:Optional[DetectionHistoryEntry] = None
        self.EntryWhereTrackedObjectWasDetectedLast:Optional[DetectionHistoryEntry] = None

    def CheckClip(self, frame: np.ndarray, timestamp: int, detections: list[Detection]) -> Optional[list[DetectionHistoryEntry]]:

        entry = DetectionHistoryEntry(detections, timestamp, frame)
        self.history.append(entry)

        hasTrackedObject = any(detection.Label in self.config.TrackedObjectsLabels for detection in detections)
        thereIsATrackedObjectInHistory = self.EntryWhereTrackedObjectWasDetectedLast is not None
        timeSinceLastTrackedObjectIsAboveLimit = (entry.Timestamp - self.EntryWhereTrackedObjectWasDetectedLast.Timestamp) > self.config.AllowedTrackedObjectGapsDuration if thereIsATrackedObjectInHistory and not hasTrackedObject else False
        clipExceedsMaxDuration = (entry.Timestamp - self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp) + self.config.PaddingStart > self.config.MaximumClipLength if thereIsATrackedObjectInHistory else False
        clipIsLongEnough = (self.EntryWhereTrackedObjectWasDetectedLast.Timestamp - self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp) > self.config.MinimumClipLengthWithoutPadding if thereIsATrackedObjectInHistory else False

        match (hasTrackedObject,thereIsATrackedObjectInHistory,timeSinceLastTrackedObjectIsAboveLimit, clipExceedsMaxDuration, clipIsLongEnough):
            case (_, True, _, True, _):
                # The clip became too long already -> output
                #log('The clip became too long already -> output')
                clipBegin = self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp - self.config.PaddingStart
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
                self.logger.debug('Detected the first object for a potential new clip.')
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
                clipBegin = self.EntryWhereTrackedObjectWasDetectedFirst.Timestamp - self.config.PaddingStart
                clipEnd = self.EntryWhereTrackedObjectWasDetectedLast.Timestamp + self.config.PaddingEnd
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