from logging import Logger
import threading

from ClipDatabase.ClipDatabase import ClipDatabase
from Surveillance.DetectionBroadcaster import DetectionBroadcaster
from Video.ClipSaver import ClipSaver
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
from Config.Config import Config
from Camera.Camera import Camera
from Surveillance.History.DetectionHistory import DetectionHistory
from Surveillance.ObjectDetection.ObjectDetection import ObjectDetector


class FrameAnalyzer:
    def __init__(self, 
                 detector:ObjectDetector, 
                 camera:Camera, 
                 detectionBroadcaster: DetectionBroadcaster,
                 detectionHistory: DetectionHistory, 
                 clipSaver: ClipSaver,
                 clipDatabase: ClipDatabase,
                 config: Config,
                 logger: Logger):
        self.detector = detector
        self.camera = camera
        self.detectionBroadcaster = detectionBroadcaster
        self.history = detectionHistory
        self.clipSaver = clipSaver
        self.clipDatabase = clipDatabase
        self.config = config
        self.logger = logger
        self.stopRequested = False

    def Start(self) -> None:
        self.thread = threading.Thread(target=self.analyzeFrames, daemon=True)
        self.thread.start()
        self.stopRequested = False
        
    def Stop(self) -> None:
        self.stopRequested = True

    def analyzeFrames(self) -> None:
        self.logger.info('Started Frame Analyses')
        
        while True and not self.stopRequested:
            objectDetectionFrame = self.camera.CaptureObjectDetectionFrame()
            detections = self.detector.Detect(objectDetectionFrame.Frame)
            self.detectionBroadcaster.Broadcast(detections)
            optionalClip = self.history.CheckClip( DetectionHistoryEntry(detections,objectDetectionFrame.Timestamp,objectDetectionFrame.Frame) )
            if optionalClip is not None:
                result = self.clipSaver.Save(optionalClip)
                self.clipDatabase.Add(result)
                self.logger.info(f'A new clip was saved. Duration:{result.ClipDuration.total_seconds:.1f}s Date:{result.DateOfRecording.strftime("%d.%m.%Y, %H:%M:%S")}')
                
        
    

            
        
        
    