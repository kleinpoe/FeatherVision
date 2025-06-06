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
        self.Database = Config.DatabaseConfig(self.Storage)
        
    class WebContentConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig'):
            self.Directory: str = os.path.join(storageConfig.ApplicationDataDirectory, 'WebInterfaceData') # The directory containing all the html files of the web interface
            self.StaticDirectory: str = os.path.join(self.Directory, 'static')
            self.DefaultThumbnail = os.path.join(self.Directory, 'DefaultThumbnail.jpg')    
            self.IndexHtml = os.path.join(self.Directory, 'stream.html')    
            self.WatchClipHtml = os.path.join(self.Directory, 'watch.html')    
            self.BrowseClipsHtml = os.path.join(self.Directory, 'browse.html')    
    
    class WebInterfaceConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig', runtimeConfig: RuntimeConfig):
            self.Content: Config.WebContentConfig = Config.WebContentConfig(storageConfig)
            self.Ip: str = runtimeConfig.Ip # Raspberry IP
            self.Port:int = 8000 # The port for the web interface
            
    class LoggingConfig:
        def __init__(self):
            self.LogToFile = True # Enable logging to a file and not just console
            self.MaximumLogBytes = 2000000 # The maximum byte size of the log file
            self.LogBackupFiles = 5 # The Backup log files count
            self.PerformanceMonitorLoggingInterval = timedelta(minutes=5) # Interval in which performance logging is done
            self.LogLevel = logging.DEBUG # The logging level, Info is probably best
            
    class CameraConfig:
        def __init__(self):
            self.MainResolution = (1920,1080) # Resolution of Web Interface Stream and saved videos. Tested is 1920x1080
            self.ObjectDetectionResolution = (854,480) # Resolution with which object detection is performed. Tested is 854x480
            self.Fps = 30 # The FramesRate (Frames per second) with which the main camera stream operates. Tested is 30
    
    class ClipGenerationConfig:
        def __init__(self):
            self.TrackedObjectsLabels = ['bird', 'squirrel', 'cat', 'dog', 'horse', 'bear'] # These must align with the given object detections labels file
            # It is possible to configure this so it will not work. Clip Padding must be smaller than max duration without tracked objects. Also history must have enough entries to hold more than max clip duration
            self.PaddingStart = timedelta(seconds=2)  # Prepend this duration to video before first detection
            self.PaddingEnd = timedelta(seconds=2)  # Append this duration to video after last detection
            self.MaximumClipLength = timedelta(seconds=60)  # Maximum video length (if detection is still present after save will make another one)
            self.MinimumClipLengthWithoutPadding = timedelta(seconds=2)  # If a potential clip has a consecutive duration of tracked objects (including allowed gaps) below this limit, it will not be saved 
            self.AllowedTrackedObjectGapsDuration = timedelta(seconds=5)  # When a tracked objects leaves the video, we keep on recording for this duration and wait that maybe detection comes back. (Must be larger than clip padding!)
            self.DetectionHistoryMaxEntries = 2000 # The number of frames the object detection history will hold. It must be shorter than what the high-resolution frame buffer can hold but longer than the max video length. Raspi 5 can handle ~5 fps object detection (might vary between object detection models)
            self.HighResolutionFrameBufferDuration = timedelta(minutes=5) # The duration of the high-resolution frame buffer. Must be longer than max clip duration. One frame occupies roughly 20-40kb (Full HD)
            
            self.MinimumScore = 0.3  # Threshold when score for a detected tracked object will be enough to consider them for clip 0 - 1
            self.DetectionHistoryMinimumScore = 0.3 # Minimum score under which a detection will be completely discarded
            self.MinimumScoreForAnnotatedClip = 0.3 # Minimum score for a detection to appear in the annotated clip (can be used to determine right threshold, should be lower than MinimumScore)
            self.ShowAlsoUntrackedObjectsInAnnotatedClip = True
            self.MinimumScoreForStream = 0.3 # Minimum score for a detection to be streamed
            self.ShowAlsoUntrackedObjectsInStream = True
            
            self.FilterStaticObjects = True # If an object is constantly detected, it can be removed automatically, otherwise you may get unlimited recordings
            self.StaticObjectThreshold = 0.02 # In percent relative to the image width/height, if the border of the detected rectangle is in this threshold it is assumed to be equal. 
            self.ObjectIsStaticWhenDetectedLongerThan = timedelta(seconds=30) # If a detection is present for more than this time, ignore it.
            self.ObjectIsNotStaticAnymoreWhenNotPresentFor = timedelta(seconds=600) # If a static object is not present for this time, it is not considered as static anymore

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
            self.DatabaseDirectory = os.path.join(self.ApplicationDataDirectory, 'Database')
            self.ArchiveDuration = timedelta(days=7)
            self.MaximumStorageOccupationForSaving = 95  # 0-100%
            
    class DetectionConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig'):
            self.TensorFlowModelFilePath = os.path.join(storageConfig.TensorFlowModelDirectory, 'efficientdetlite2.tflite')
            self.LabelsFilePath = os.path.join(storageConfig.TensorFlowModelDirectory, 'coco_labels.txt')
            
    class DatabaseConfig:
        def __init__(self, storageConfig: 'Config.StorageConfig'):
            self.ClipDatabaseFilePath = os.path.join(storageConfig.DatabaseDirectory, 'Clips.json')

    