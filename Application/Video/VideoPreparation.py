from dataclasses import dataclass
from datetime import datetime
import os
from statistics import mean
import cv2

from Infrastructure.Clock import Clock
from Config.Config import Config
from ObjectDetection.FrameAnnotator import FrameAnnotator
from ObjectDetection.DetectionHistoryEntry import DetectionHistoryEntry

@dataclass
class AnnotatedClipInfo:
    FilePath:str
    Timestamp:datetime
    
class RecordingFilePathProvider:
    def __init__(self, config: Config):
        self.config = config
    
    def getDirectory(self, timestamp:datetime):
        clipDirectory = self.config.Storage.ClipsDirectory
        yearDirectoryName = str(timestamp.year)
        monthDirectoryName = str(timestamp.month)
        dayDirectoryName = str(timestamp.day)
        return os.path.join(clipDirectory, yearDirectoryName, monthDirectoryName, dayDirectoryName)
    
    def getFileName(self,timestamp:datetime, suffix:str, extension:str):
        formattedTimestamp = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        return f'Clip_{formattedTimestamp}_{suffix}.{extension}'
    
    def getFilePath(self, timestamp:datetime, suffix:str, extension:str ):
        directory = self.getDirectory(timestamp)
        fileName = self.getFileName(timestamp, suffix, extension)
        return os.path.join(directory, fileName)
    
    def GetThumbnailFilePath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'Thumbnail', extension)
    
    def GetHighResClipPath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'HighResolution', extension)
    
    def GetAnnotatedClipPath(self, timestamp:datetime, extension:str)->str:
        return self.getFilePath(timestamp, 'Annotated', extension)

class AnnotatedClipSaver:
    def __init__(self, frameAnnotator: FrameAnnotator, clock: Clock, config: Config):
        self.frameAnnotator = frameAnnotator
        self.config = config
        self.clock = clock
    
    def getFilePath(self):
        directory = self.config.Storage.
        return f''
    
    def SaveAnnotatedClip(self, entries: list[DetectionHistoryEntry]):
        
        annotatedFrames = [self.frameAnnotator.AnnotateDetectedObjects(x.Frame,x.Detections) for x in entries]
        height,width,_ = annotatedFrames[0].shape
        estimatedFps = 1 / mean([(f2.Timestamp - f1.Timestamp).total_seconds() for f1, f2 in zip(entries, entries[1:])])

        print(f'Writing annotated Clip: W{width}xH{height} FPS{estimatedFps} Frames{len(annotatedFrames)} Duration{(entries[-1].Timestamp-entries[0].Timestamp)}')
        
        codec = cv2.VideoWriter.fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter('testAnnotate.mp4',codec,estimatedFps,(width,height))
        for frame in annotatedFrames:
            videoWriter.write(frame)
        videoWriter.release()