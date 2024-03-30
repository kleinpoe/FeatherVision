from dataclasses import dataclass
from datetime import timedelta
import logging
import os

from Config.RuntimeConfig import RuntimeConfig


class Config:
    def __init__(self, runtimeConfig: RuntimeConfig):
        
        self.Logging = Config.LoggingConfig()
        self.ClipGeneration = Config.ClipGenerationConfig()
        self.Location = Config.LocationConfig()
        self.Storage = Config.StorageConfig(runtimeConfig)
        self.Camera = Config.CameraConfig()
        self.Detection = Config.DetectionConfig(self.Storage)
        self.WebInterface = Config.WebInterfaceConfig(self.Storage,runtimeConfig)
        
    class WebContentConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig'):
            self.Directory: str = os.path.join(storageConfig.ApplicationDataDirectory, 'WebInterfaceData') # The directory containing all the html files of the web interface
            self.StaticDirectory: str = os.path.join(self.Directory, 'static')
            self.DefaultThumbnail = os.path.join(self.Directory, 'DefaultThumbnail.jpg')    
            self.IndexHtml = os.path.join(self.Directory, 'index.html')    
    
    class WebInterfaceConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig', runtimeConfig: RuntimeConfig):
            self.Content: Config.WebContentConfig = Config.WebContentConfig(storageConfig)
            self.Ip: str = runtimeConfig.Ip
            self.Port:int = 8000 # The port for the web interface
            
    class LoggingConfig:
        def __init__(self):
            self.LogToFile = True
            self.MaximumLogBytes = 2000000
            self.LogBackupFiles = 5
            self.PerformanceMonitorLoggingInterval = timedelta(minutes=10)
            self.LogLevel = logging.DEBUG
            
    class CameraConfig:
        def __init__(self):
            self.MainResolution = (1920,1080) # Resolution of Web Interface Stream and saved videos
            self.ObjectDetectionResolution = (854,480) # Resolution with which object detection is performed
            self.Fps = 30 # The FramesRate (Frames per second) with which the main camera stream operates
    
    class ClipGenerationConfig:
        def __init__(self):
            self.TrackedObjectsLabels = ['bird', 'squirrel', 'cat', 'dog', 'horse', 'bear'] # These must align with the given object detections labels file
            self.MinimumScore = 0.4  # Threshold when score for a detected tracked object will be enough to consider them for clip 0 - 1
            # It is possible to configure this so it will not work. Clip Padding must be smaller than max duration without tracked objects. Also history must have enough entries to hold more than max clip duration
            self.PaddingStart = timedelta(seconds=2)  # Prepend this duration to video before first detection
            self.PaddingEnd = timedelta(seconds=2)  # Append this duration to video after last detection
            self.MaximumClipLength = timedelta(seconds=60)  # Maximum video length (if detection is still present after save will make another one)
            self.MinimumClipLengthWithoutPadding = timedelta(seconds=3)  # If a potential clip has a consecutive duration of tracked objects (including allowed gaps) below this limit, it will not be saved 
            self.AllowedTrackedObjectGapsDuration = timedelta(seconds=5)  # When a tracked objects leaves the video, we keep on recording for this duration and wait that maybe detection comes back
            self.DetectionHistoryMaxEntries = 5000 # The number of frames the object detection history will hold. It must be shorter than what the high-resolution frame buffer can hold but longer than the max video length. Raspi 5 can handle ~5 fps object detection (might vary between object detection models)
            self.HighResolutionFrameBufferDuration = timedelta(minutes=5) # The duration of the high-resolution frame buffer. Must be longer than max clip duration.
            # AnnotatedClipSettings
            self.MinimumScoreForAnnotatedClip = 0.4
            self.ShowAlsoUntrackedObjectsInAnnotatedClip = True

    class LocationConfig:
        def __init__(self):
            # Necessary to detect when sun is up
            self.Latitude = 49.71754
            self.Longitude = 11.05877    
    
    class StorageConfig:
        def __init__(self, runtimeConfig: RuntimeConfig):
            self.ApplicationDataDirectory = os.path.join(runtimeConfig.ApplicationDirectory, 'ApplicationData')
            self.LogFileDirectory = os.path.join(self.ApplicationDataDirectory, 'LogFiles')
            self.LogFilePath = os.path.join(self.LogFileDirectory, 'log.txt')
            self.ClipsDirectory = os.path.join(self.ApplicationDataDirectory, 'Clips')
            self.TensorFlowModelDirectory = os.path.join(self.ApplicationDataDirectory, 'TensorflowLiteModels')
            self.ArchiveDuration = timedelta(days=7)
            self.MaximumStorageOccupationForSaving = 95  # 0-100%
            
    class DetectionConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig'):
            self.TensorFlowModelFilePath = os.path.join(storageConfig.TensorFlowModelDirectory, 'mobilenet_v2.tflite')
            self.LabelsFilePath = os.path.join(storageConfig.TensorFlowModelDirectory, 'coco_labels.txt')
            

    