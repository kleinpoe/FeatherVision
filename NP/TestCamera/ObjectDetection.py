from dataclasses import dataclass
from typing import Optional
import tflite_runtime.interpreter as tflite
import cv2
import numpy as np

@dataclass
class ModelDetails:
    IsFloatingPointModel:bool
    InputImageSize:tuple[int,int]
    InputTensorIndex:int
    
@dataclass
class Rectangle:
    Position:tuple[float,float]
    Size:tuple[float,float]
    @property
    def Width(self):
        return self.Size[0]
    @property
    def Height(self):
        return self.Size[1]
    @property
    def Top(self):
        return self.Size[1]
    @property
    def Left(self):
        return self.Size[1]
    @property
    def Bottom(self):
        return self.Size[1]
    @property
    def Right(self):
        return self.Size[1]
    @classmethod 
    def FromPadding(cl, topLeftBottomRight:tuple[int,int,int,int]) -> 'Rectangle':
        top, left, bottom, right = topLeftBottomRight
        actualLeft = min(left,right)
        actualRight = max(left,right)
        actualTop = min(top,bottom)
        actualBottom = max(top,bottom)
        return Rectangle(Position=(actualTop,actualLeft), Size=(actualBottom-actualTop, actualRight-actualLeft))

@dataclass
class Detection:
    BoundingBox:Rectangle
    Score:float
    LabelIndex:int
    Label:Optional[str]
    


class ObjectDetection:
    
    def __init__(self, modelFilePath: str, labelsFilePath: str):
        self.interpreter = tflite.Interpreter(model_path=modelFilePath, num_threads=2)
        self.interpreter.allocate_tensors()
        inputDetails = self.interpreter.get_input_details()
        self.modelDetails = ModelDetails(IsFloatingPointModel=inputDetails[0]['dtype'] == np.float32,
                                         InputImageSize=(inputDetails[0]['shape'][1],inputDetails[0]['shape'][2]),
                                         InputTensorIndex=inputDetails[0]['index'])
        self.Labels = self.readLabels(labelsFilePath)

    def readLabels(self, filePath:str)-> dict[int,str] :
        with open(filePath,'r') as file:
            lines = file.readlines()
        return {int(splitted[0]):splitted[1] for splitted in [line.split() for line in lines]  }
    
    def Detect(self, image:np.ndarray) -> list[Detection]:
        
        image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
        resized = cv2.resize(image, self.modelDetails.InputImageSize)
        expanded = np.expand_dims(resized, axis=0)
        if self.modelDetails.IsFloatingPointModel:
            expanded = (np.float32(expanded) - 127.5) / 127.5 # Todo change to avg and scale with std
        
        self.interpreter.set_tensor(self.modelDetails.InputTensorIndex, expanded)
        self.interpreter.invoke()
        
        outputDetails = self.interpreter.get_output_details()
        detectedBoxes = self.interpreter.get_tensor(outputDetails[0]['index'])[0]
        detectedClasses = self.interpreter.get_tensor(outputDetails[1]['index'])[0]
        detectedScores = self.interpreter.get_tensor(outputDetails[2]['index'])[0]
        
        return [Detection(BoundingBox=Rectangle.FromPadding(topLeftBottomRight=detectedBoxes[i]),
                          Score = detectedScores[i],
                          LabelIndex = detectedClasses[i],
                          Label = None if self.Labels is None else self.Labels[detectedClasses[i]] ) 
                for i in range(0,len(detectedBoxes))]
