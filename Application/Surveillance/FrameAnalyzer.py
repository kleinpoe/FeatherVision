from logging import Logger
import threading

from Infrastructure.PerformanceMonitor import PerformanceMonitor
from Surveillance.History.StaticDetectionFilter import StaticDetectionFilter
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
                 staticFilter:StaticDetectionFilter,
                 camera:Camera, 
                 detectionBroadcaster: DetectionBroadcaster,
                 detectionHistory: DetectionHistory, 
                 clipSaver: ClipSaver,
                 clipDatabase: ClipDatabase,
                 performanceMonitor: PerformanceMonitor,
                 config: Config,
                 logger: Logger):
        self.detector = detector
        self.staticFilter = staticFilter
        self.camera = camera
        self.detectionBroadcaster = detectionBroadcaster
        self.history = detectionHistory
        self.clipSaver = clipSaver
        self.clipDatabase = clipDatabase
        self.performanceMonitor = performanceMonitor
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
            try:
                objectDetectionFrame = self.camera.CaptureObjectDetectionFrame()
                detections = self.detector.Detect(objectDetectionFrame.Frame)
                detections = [x for x in detections if x.Score > self.config.ClipGeneration.DetectionHistoryMinimumScore and not self.staticFilter.IsStatic(x, objectDetectionFrame.Timestamp)]
                #print(self.staticFilter.entries)
                self.detectionBroadcaster.Broadcast(detections)
                optionalClip = self.history.CheckClip( DetectionHistoryEntry(detections,objectDetectionFrame.Timestamp,objectDetectionFrame.Frame) )
                if optionalClip is not None:
                    result = self.clipSaver.Save(optionalClip)
                    self.clipDatabase.Add(result)
                    self.logger.info(f'A new clip was saved. Duration:{result.ClipDuration.total_seconds:.1f}s Date:{result.DateOfRecording}')
                    if self.performanceMonitor.GetHddUsageInPercent > self.config.Storage.MaximumStorageOccupationForSaving:
                        self.logger.info(f'The Storage is Low. Occupied: {self.performanceMonitor.GetHddUsageInPercent:.1f}%, Maximum: {self.config.Storage.MaximumStorageOccupationForSaving:.1f}%. Deleting Oldest Clips.')
                    while self.performanceMonitor.GetHddUsageInPercent > self.config.Storage.MaximumStorageOccupationForSaving:
                        self.clipDatabase.RemoveOldest()
            except Exception as e:
                self.logger.error("An exception occured during frame analysis")
                self.logger.exception(e)
                
        
    

            
        
        
    