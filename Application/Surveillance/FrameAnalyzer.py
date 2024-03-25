from dataclasses import dataclass
from logging import Logger
from statistics import mean
import subprocess
from typing import Callable
import cv2

from Application.Infrastructure.Clock import Clock
from Video.Saving.AnnotatedClipSaver import AnnotatedClipSaver
from ObjectDetection.Detection import Detection
from Surveillance.History.DetectionHistoryEntry import DetectionHistoryEntry
from Config.Config import Config
from Camera.Camera import Camera
from Application.Video.FrameAnnotator import FrameAnnotator
from Application.Surveillance.History.DetectionHistory import DetectionHistory
from Camera.Outputs import CircularBufferOutput
from Application.Surveillance.ObjectDetection.ObjectDetection import ObjectDetector

from picamera2 import Picamera2


class FrameAnalyzer:
    def __init__(self, 
                 detector:ObjectDetector, 
                 camera:Camera, 
                 broadcastDetections: Callable[[list[Detection]],None],
                 circularBuffer: CircularBufferOutput, 
                 frameAnnotator: FrameAnnotator, 
                 detectionHistory: DetectionHistory, 
                 annotatedClipSaver: AnnotatedClipSaver,
                 config: Config,
                 logger: Logger,
                 clock: Clock):
        self.config = config
        self.detector = detector
        self.camera = camera
        self.broadcastDetections = broadcastDetections
        self.history = detectionHistory
        self.annotatedClipSaver = annotatedClipSaver
        self.circularBuffer = circularBuffer
        self.frameAnnotator = frameAnnotator
        self.logger = logger
        self.clock = clock

    def AnalyzeFrames(self):
        self.logger.info('Started Frame Analyses')
        
        while True:
            
            objectDetectionFrame = self.camera.CaptureObjectDetectionFrame()
            results = self.detector.Detect(objectDetectionFrame.Frame)
            
            resultsOverThresholdScore = [result for result in results if result.Score > self.config.ClipGeneration.MinimumScore]
            self.broadcastDetections(resultsOverThresholdScore)
            
            optionalClip = self.history.CheckClip( DetectionHistoryEntry(resultsOverThresholdScore,objectDetectionFrame.Timestamp,objectDetectionFrame.Frame) )
            
            if optionalClip is not None:
                
                
                print('Detected save-worthy clip!')
                
                timestamp = self.clock.Now()
                self.annotatedClipSaver.Save(timestamp, optionalClip)
                
                
                richFrames = self.circularBuffer.GetFrames(optionalClip[0].Timestamp, optionalClip[-1].Timestamp)
                
                videoPath = 'test.h264'
                convertedPath = 'test.mp4'
                print(f"Writing frames to {videoPath}")
                # Write Circular Buffer to h264 file
                with open(videoPath, "wb") as file:
                    size = 0
                    length = len(richFrames)
                    for richFrame in richFrames:
                        file.write(richFrame.Frame)
                        size = size + len(richFrame.Frame)
                print(f"Done. Length = {size/1E6}Mb. {length/1E6}s")

                # Convert h264 file to mp4
                print("Converting file to mp4")
                command = f"ffmpeg -loglevel error -r {30} -i {videoPath} -movflags +faststart -y -c copy {convertedPath}"
                returnCode = subprocess.call(command.split(" "))
                print(f"Conversion done {returnCode}")
                #command = ['ffmpeg', '-y', '-loglevel', 'error', '-i', videoPath, '-movflags', '+faststart', '-c:v', 'copy', convertedPath]
                #subprocess.call(command)
    

            
        
        
    