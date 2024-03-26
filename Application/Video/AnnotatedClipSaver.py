from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from pathlib import Path
from statistics import mean
import cv2

from Video.FilePathProvider import FilePathProvider
from Config.Config import Config
from Video.FrameAnnotator import FrameAnnotator
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
    
class AnnotatedClipSaver:
    def __init__(self, filePathProvider: FilePathProvider, frameAnnotator: FrameAnnotator, logger: Logger, config: Config):
        self.frameAnnotator = frameAnnotator
        self.config = config
        self.filePathProvider = filePathProvider
        self.logger = logger
    
    def Save(self, timestamp:datetime, entries: list[DetectionHistoryEntry]):
        
        filePath = self.filePathProvider.GetAnnotatedClipPath(timestamp, 'mp4')
        
        Path(filePath).parent.mkdir(parents=True, exist_ok=True)
        
        annotatedFrames = [self.frameAnnotator.AnnotateDetectedObjects(x.Frame,x.Detections) for x in entries]
        height,width,_ = annotatedFrames[0].shape
        estimatedFps = 1 / mean([(f2.Timestamp - f1.Timestamp).total_seconds() for f1, f2 in zip(entries, entries[1:])])

        self.logger.info(f'Writing annotated Clip: W{width}xH{height} FPS{estimatedFps:.1f} Frames{len(annotatedFrames)} Duration{(entries[-1].Timestamp-entries[0].Timestamp)}')
        
        codec = cv2.VideoWriter.fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter(filePath,codec,estimatedFps,(width,height))
        for frame in annotatedFrames:
            videoWriter.write(frame)
        videoWriter.release()
        
        return filePath
        
