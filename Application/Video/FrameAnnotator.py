from dataclasses import dataclass
import numpy as np
from typing import List
import cv2
from Config.Config import Config
from Surveillance.ObjectDetection.Detection import Detection


@dataclass
class FrameAnnotationOptions:
    Margin:int
    FontSize:int
    FontThickness:int
    BoxThickness:int
    TextColor:tuple[int,int,int]
    BoxColor:tuple[int,int,int]
    Font:int
    

class FrameAnnotator:
    def __init__(self, config: Config):
        self.config = config

    def AnnotateDetectedObjects(self, imageIn: np.ndarray, detections: List[Detection]) -> np.ndarray:

        image = np.copy(imageIn)

        options =  FrameAnnotationOptions(
            Margin=10,
            FontSize=1,
            BoxThickness=1,
            FontThickness=1,
            TextColor=(240,255,255),
            BoxColor=(240,255,255),
            Font=cv2.FONT_HERSHEY_PLAIN)

        for detection in detections:
            
            if detection.Score < self.config.ClipGeneration.MinimumScoreForAnnotatedClip:
                continue
            if not self.config.ClipGeneration.ShowAlsoUntrackedObjectsInAnnotatedClip and (detection.Label not in self.config.ClipGeneration.TrackedObjectsLabels):
                continue
            
            
            height,width,_ = image.shape
            topLeftPoint = int(detection.BoundingBox.Left * width), int(detection.BoundingBox.Top * height)
            bottomRightPoint = int(detection.BoundingBox.Right * width), int(detection.BoundingBox.Bottom * height)
            cv2.rectangle(image, 
                          topLeftPoint, 
                          bottomRightPoint, 
                          options.BoxColor, 
                          options.BoxThickness)

            text = f'{detection.Label} ({detection.Score * 100:02.0f}%)'
            textLocation = int(options.Margin + detection.BoundingBox.Left* width),int( detection.BoundingBox.Bottom* height - options.Margin)
            cv2.putText(image, 
                        text, 
                        textLocation, 
                        options.Font,
                        options.FontSize, 
                        options.TextColor, 
                        options.FontThickness)
        return image