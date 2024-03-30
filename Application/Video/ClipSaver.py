from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import Logger

from Surveillance.ObjectDetection.Detection import Detection
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
from Config.Config import Config
from Infrastructure.Clock import Clock
from Video.AnnotatedClipSaver import AnnotatedClipSaver
from Video.HighResClipSaver import HighResClipSaver
from Video.ThumbnailSaver import ThumbnailSaver

    
@dataclass
class DetectionsInClip:
    Time: timedelta
    Detections: list[Detection]

class ClipSaver:
    def __init__(self, 
                 highResClipSaver: HighResClipSaver, 
                 annotatedClipSaver: AnnotatedClipSaver,
                 thumbnailSaver: ThumbnailSaver,
                 clock: Clock,
                 logger: Logger, 
                 config: Config):
        self.highResClipSaver = highResClipSaver
        self.annotatedClipSaver = annotatedClipSaver
        self.thumbnailSaver = thumbnailSaver
        self.clock = clock
        self.logger = logger
        self.config = config
        
    @dataclass
    class Result:
        ThumbnailFilePath:str
        HighResClipFilePath:str
        AnnotatedClipFilePath:str
        ClipDuration: timedelta
        Datetime: datetime
        Detections: list[DetectionsInClip]
    
        
    def Save(self, detectionHistoryEntries:list[DetectionHistoryEntry]) -> Result:
        timestamp = detectionHistoryEntries[0].Timestamp
        annotatedPath = self.annotatedClipSaver.Save(timestamp, detectionHistoryEntries)
        highResResult = self.highResClipSaver.Save(timestamp,detectionHistoryEntries[0].Timestamp, detectionHistoryEntries[-1].Timestamp )
        thumbnailPath = self.thumbnailSaver.Save(timestamp, detectionHistoryEntries)
        detections = [DetectionsInClip(x.Timestamp-detectionHistoryEntries[0].Timestamp,x.Detections) for x in detectionHistoryEntries]
        return ClipSaver.Result(thumbnailPath, highResResult.FilePath, annotatedPath, highResResult.Duration, timestamp,detections)