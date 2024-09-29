from datetime import datetime
from logging import Logger
from Surveillance.ObjectDetection.Rectangle import Rectangle
from Config.Config import Config
from Surveillance.ObjectDetection.Detection import Detection


class Entry:
    def __init__(self, detection: Detection, timestamp: datetime, config: Config, logger:Logger):
        self.IsStatic = False
        self.BoundingBox = detection.BoundingBox
        self.Label = detection.Label
        self.FirstDetectionTime = timestamp
        self.LastDetectionTime = timestamp
        self.config = config
        self.logger = logger
        
    def IsSimilarIfYesUpdateIsStatic(self, detection: Detection, timestamp: datetime) -> bool:
        threshold = self.config.ClipGeneration.StaticObjectThreshold
        otherBoundingBox = detection.BoundingBox
        rectangleDifferences = [abs(self.BoundingBox.Bottom - otherBoundingBox.Bottom),
                                abs(self.BoundingBox.Left - otherBoundingBox.Left),
                                abs(self.BoundingBox.Top - otherBoundingBox.Top),
                                abs(self.BoundingBox.Right - otherBoundingBox.Right)]
        rectangleIsSimilar = all([x < threshold for x in rectangleDifferences])
        labelIsSimilar = self.Label == detection.Label
        isSimilar = rectangleIsSimilar and labelIsSimilar
        if isSimilar:
            #self.logger.info(f'Found similar object {rectangleDifferences}, {threshold}, {self.Label}')
            self.LastDetectionTime = timestamp
            self.BoundingBox = Rectangle.Average(self.BoundingBox, otherBoundingBox)
            if not self.IsStatic:
                self.IsStatic = (self.LastDetectionTime - self.FirstDetectionTime) > self.config.ClipGeneration.ObjectIsStaticWhenDetectedLongerThan
                if self.IsStatic:
                    self.logger.info(f"The object <{self.Label}> at [T {self.BoundingBox.Top:.2f},L {self.BoundingBox.Left:.2f},B {self.BoundingBox.Bottom:.2f},R {self.BoundingBox.Right:.2f}] first detected at {self.FirstDetectionTime} is now considered as static.")
        return isSimilar
    
    def MustBeRemoved(self, timestamp: datetime):
        staticAndNotDetectedForLong = self.IsStatic and (timestamp - self.LastDetectionTime) > self.config.ClipGeneration.ObjectIsNotStaticAnymoreWhenNotPresentFor 
        notYetStaticAndNotDetectedForShort = not self.IsStatic and (timestamp - self.LastDetectionTime) > self.config.ClipGeneration.AllowedTrackedObjectGapsDuration
        if staticAndNotDetectedForLong:
            self.logger.info(f"The static object <{self.Label}> at [T {self.BoundingBox.Top:.2f},L {self.BoundingBox.Left:.2f},B {self.BoundingBox.Bottom:.2f},R {self.BoundingBox.Right:.2f}] first detected at {self.FirstDetectionTime}, not detected since {self.LastDetectionTime} is now considered as not static anymore.")
        return staticAndNotDetectedForLong or notYetStaticAndNotDetectedForShort
    
    def __repr__(self):
        return f'<StaticEntry IsStatic={self.IsStatic} Label={self.Label} LastDetection={self.LastDetectionTime}>'
        

class StaticDetectionFilter:

    def __init__(self, config:Config, logger:Logger):
        self.config = config
        self.logger = logger
        self.entries: list[Entry] = []
        
    def IsStatic(self, detection: Detection, timestamp: datetime) -> bool:
        #self.logger.info(f"Checking object {detection.Label}")
        for entry in self.entries:
            isSimilar = entry.IsSimilarIfYesUpdateIsStatic(detection, timestamp)
            if isSimilar:
                return entry.IsStatic
        self.entries.append(Entry(detection, timestamp, self.config, self.logger))
        self.entries = [x for x in self.entries if not x.MustBeRemoved(timestamp)]
        return False