from dataclasses import dataclass
from datetime import timedelta
import logging
import os

from Config.Environment import Environment


@dataclass
class Config:
    def __init__(self):
        self.WebInterfaceConfig = WebInterfaceConfig()
        self.LoggingConfig = LoggingConfig()
        self.DetectionConfig = DetectionConfig()
        self.LocationConfig = LocationConfig()
        self.StorageConfig = StorageConfig()
        
    
@dataclass
class WebInterfaceConfig:
    Port:int = 8000 # The port for the web interface
    HtmlDirectory:str = os.path.join(Environment.GetApplicationDirectory(), 'Html') # The directory containing all the html files of the web interface
    FaviconFilePath:str = os.path.join(HtmlDirectory, 'favicon.ico') # The filepath of the favicon icon of the web interface
    DefaultThumbnail = os.path.join(HtmlDirectory, 'Assets', 'DefaultThumbnail.jpg')
    
@dataclass    
class LoggingConfig:
    LogToFile = True
    MaximumLogBytes = 2000000
    LogBackupFiles = 5
    PerformanceMonitorLoggingIntervalInSeconds = 600
    LogLevel = logging.DEBUG
    
@dataclass
class DetectionConfig:
    DetectionQuality = 1  # 0:worst/fastest - 3:best/slowest
    TensorFlowTrainingData = os.path.join(Environment.GetApplicationDirectory(), 'TensorflowModels', f'efficientdet_lite{DetectionQuality}.tflite')
    ObjectsToDetect = ['bird', 'squirrel', 'cat', 'dog', 'horse', 'bear']
    MinimumBirdScore = 0.2  # Threshold when confidence for bird detection will be enough 0 - 1
    SecondsWithoutBird = 5.0  # Keep on recording for this time and wait that maybe detection comes back
    SecondsStart = 2.0  # Prepend this many seconds to video before first detection
    SecondsEnd = 2.0  # Append this many seconds to video after last detection
    MaxVideoSeconds = 60.0  # Maximum video length (if detection is still present after save will make another one)
    MinSecondsWithBird = 3  # Will not save videos for detections with less than a total length ofs

@dataclass
class LocationConfig:
    # Necessary to detect when sun is up
    Latitude = 49.71754
    Longitude = 11.05877    
    
@dataclass
class StorageConfig:
    ApplicationDataDirectory = os.path.join(Environment.GetApplicationDirectory(), 'ApplicationData')
    LogFileDirectory = os.path.join(ApplicationDataDirectory, 'LogFiles')
    LogFilePath = os.path.join(LogFileDirectory, 'log.txt')
    OutputDirectory = os.path.join(ApplicationDataDirectory, 'Recordings')
    ThumbnailDirectory = os.path.join(ApplicationDataDirectory, 'RecordingThumbnails')
    ArchiveDirectory = os.path.join(ApplicationDataDirectory, 'RecordingArchive')
    ArchiveDuration = timedelta(days=7)
    MaximumStorageOccupationForSaving = 95  # 0-100%

    