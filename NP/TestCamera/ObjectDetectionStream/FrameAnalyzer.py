from dataclasses import dataclass
from statistics import mean
import subprocess
from typing import Callable, Optional
import cv2
import numpy as np

from FrameAnnotator import FrameAnnotator
from DetectionHistory import DetectionHistory
from StreamOutput import CircularBufferOutput, StreamOutput
from ObjectDetection import Detection, ObjectDetector

from picamera2 import Picamera2

from log import log


class FrameAnalyzer:
    def __init__(self, detector:ObjectDetector, picamera:Picamera2, broadcastDetections: Callable[[list[Detection]],None], getCurentTimestamp: Callable[[],int], circularBuffer: CircularBufferOutput, frameAnnotator: FrameAnnotator):
        self.detector = detector
        self.camera = picamera
        self.broadcastDetections = broadcastDetections
        self.history = DetectionHistory(maxEntries=100000, labelsOfTrackedObjects=["bird"])
        self.getCurentTimestamp = getCurentTimestamp
        self.circularBuffer = circularBuffer
        self.frameAnnotator = frameAnnotator

    def AnalyzeFrames(self):
        log('Started Frame Analyses')
        while True:
            #log(f'Capturing New LoRes-Frame')
            
            request = self.camera.capture_request()
            frame = request.make_array(name='lores')
            #metadata = request.get_metadata()
            request.release()
            timestamp = self.getCurentTimestamp()
            #log(f'Captured New LoRes-Frame: NumberOfBytes={len(frame)}, Timestamps[{timestamp1}-{timestamp2}] TimeStamp={timestamp}µs')
            
            rgbFrame = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)[:,:854,:]
            
            results = self.detector.Detect(rgbFrame)
            #log([(result.Label,result.Score) for result in results])
            resultsOverThresholdScore = [result for result in results if result.Score > 0.3]
            self.broadcastDetections(resultsOverThresholdScore)
            optionalClip = self.history.CheckClip(rgbFrame, timestamp, resultsOverThresholdScore)
            if optionalClip is not None:
                
                print('New Clip!')
                print(optionalClip[0])
                print(optionalClip[-1])
                
                annotatedFrames = [self.frameAnnotator.AnnotateDetectedObjects(x.Frame,x.Detections) for x in optionalClip]
                height,width,_ = annotatedFrames[0].shape
                clipFps = 1/(mean([f2.Timestamp - f1.Timestamp for f1, f2 in zip(optionalClip, optionalClip[1:])]) / 1E6)

                print(f'Writing annotated Clip: W{width}xH{height} FPS{clipFps} Frames{len(annotatedFrames)} Duration{(optionalClip[-1].Timestamp-optionalClip[0].Timestamp)/1E6:.2f}s')
                codec = cv2.VideoWriter.fourcc(*'mp4v')
                videoWriter = cv2.VideoWriter('testAnnotate.mp4',codec,clipFps,(width,height))
                for frame in annotatedFrames:
                    videoWriter.write(frame)
                videoWriter.release()
                
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
    

            
        
        
    