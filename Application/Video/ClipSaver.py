from logging import Logger

from Camera.Outputs.CircularBufferOutput import CircularBufferOutput
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
from Config.Config import Config
from Infrastructure.Clock import Clock
from Video.AnnotatedClipSaver import AnnotatedClipSaver
from Video.HighResClipSaver import HighResClipSaver
from Video.ThumbnailSaver import ThumbnailSaver



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
        
    def Save(self, detectionHistoryEntries:list[DetectionHistoryEntry], highResBuffer: CircularBufferOutput) -> Result:
        timestamp = self.clock.Now()
        annotatedPath = self.annotatedClipSaver.Save(timestamp, detectionHistoryEntries)
        highResPath = self.highResClipSaver.Save(timestamp,highResBuffer, detectionHistoryEntries[0].Timestamp, detectionHistoryEntries[-1].Timestamp )
        thumbnailPath = self.thumbnailSaver.Save(timestamp, highResPath)
        return ClipSaver.Result()