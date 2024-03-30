from pathlib import Path

import cv2
import numpy as np
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
from Config.Config import Config
from Video.FilePathProvider import FilePathProvider


import subprocess
from datetime import datetime
from logging import Logger


class ThumbnailSaver:
    def __init__(self, filePathProvider: FilePathProvider, config: Config, logger: Logger):
        self.filePathProvider = filePathProvider
        self.config = config
        self.logger = logger

    def Save(self, timestamp: datetime, detectionHistoryEntries:list[DetectionHistoryEntry]):
        
        filePath = self.filePathProvider.GetThumbnailFilePath(timestamp, 'jpg')
        Path(filePath).parent.mkdir(parents=True, exist_ok=True)
        self.logger.info(f'Creating Thumbnail at "{filePath}"')
        
        
        start = next(i for i,x in enumerate(detectionHistoryEntries) if (x.Timestamp - detectionHistoryEntries[0].Timestamp) > self.config.ClipGeneration.PaddingStart)
        end = next(i for i,x in reversed(list(enumerate(detectionHistoryEntries))) if (detectionHistoryEntries[-1].Timestamp - x.Timestamp ) > self.config.ClipGeneration.PaddingEnd)
        coreEntries = detectionHistoryEntries[start:end]
        
        numberOfFrames = len(coreEntries)
        # Putting a different number here will not work, needs adaption below
        numberOfThumbnailPictures = 4
        intervalLength = int(numberOfFrames / numberOfThumbnailPictures)
        
        previewFrames = [self.getThumbnailFrameOfInterval(coreEntries[i*intervalLength:(i+1)*intervalLength]) for i in range(0,numberOfThumbnailPictures)]
        
        (height,width,_) = previewFrames[0].Frame.shape
        outputframe = np.zeros((height*2, width*2, 3), dtype=np.uint8)
        outputframe[:height, :width] = previewFrames[0].Frame
        outputframe[:height, width:] = previewFrames[1].Frame
        outputframe[height:, :width] = previewFrames[2].Frame
        outputframe[height:, width:] = previewFrames[3].Frame
        
        cv2.imwrite(filePath, outputframe)

        # ffmpeg -ss 2 -i "20220220-145106_Birdbuddy.mp4" -frames 4 -vf "select=not(mod(n\,30)),scale=320:180,tile=2x2" -vsync vfr -q:v 10 20220220-145106_Birdbuddy.jpg
        #Path(filePath).parent.mkdir(parents=True, exist_ok=True)
        #secondsPaddingStart = self.config.ClipGeneration.PaddingStart.total_seconds()
        #frames = numberOfFramesOfHighResVideoFile
        #self.logger.info(f'Creating Thumbnail at "{filePath}" for video "{highResVideoFilePath}"')
        #command = ['ffmpeg', '-loglevel', 'error', '-ss', str(secondsPaddingStart), '-i', highResVideoFilePath, '-frames:v', '1', '-vf', f'select=not(mod(n\,{frames})),scale=320:180,tile=2x2', '-vsync', 'vfr', '-q:v', '10', filePath]
        #returnCode = subprocess.call(command)
        #if returnCode is not 0:
        #    self.logger.error(f'Error during generation of thumbnail "{filePath}" for video "{highResVideoFilePath}".')
        #    raise RuntimeError("Error during generation of thumbnail.")
        return filePath
    
    def getThumbnailFrameOfInterval(self,entries:list[DetectionHistoryEntry]):

        def getScore(entry: DetectionHistoryEntry)->float:
            matchingDetections = [x for x in entry.Detections if x.Label in self.config.ClipGeneration.TrackedObjectsLabels]
            if len(matchingDetections) == 0:
                return 0
            return max(matchingDetections, key=lambda x:x.Score).Score
        
        imageWithBestScore = max(entries, key=getScore)
        
        #for entry in entries:
        #    print(f"Entry: {entry.Timestamp} {[x for x in entry.Detections if x.Label in self.config.ClipGeneration.TrackedObjectsLabels]}")
        #print(f"Chose: {imageWithBestScore.Timestamp} {[x for x in imageWithBestScore.Detections if x.Label in self.config.ClipGeneration.TrackedObjectsLabels]}")
        
        return imageWithBestScore