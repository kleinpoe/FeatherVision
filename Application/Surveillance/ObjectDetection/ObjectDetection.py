import tflite_runtime.interpreter as tflite
import numpy as np

from Surveillance.ObjectDetection.Detection import Detection
from Surveillance.ObjectDetection.ImagePreparation import ImagePreparation
from Surveillance.ObjectDetection.ModelDetails import ModelDetails
from Surveillance.ObjectDetection.Rectangle import Rectangle

class ObjectDetector:
    
    def __init__(self, modelFilePath: str, labelsFilePath: str, imagePreparation: ImagePreparation):
        self.interpreter = tflite.Interpreter(model_path=modelFilePath, num_threads=2)
        self.interpreter.allocate_tensors()
        inputDetails = self.interpreter.get_input_details()
        self.modelDetails = ModelDetails(IsFloatingPointModel=inputDetails[0]['dtype'] == np.float32,
                                         InputImageSize=(inputDetails[0]['shape'][1],inputDetails[0]['shape'][2]),
                                         InputTensorIndex=inputDetails[0]['index'])
        self.Labels = self.readLabels(labelsFilePath)
        self.imagePreparation = imagePreparation

    def readLabels(self, filePath:str)-> dict[int,str] :
        with open(filePath,'r') as file:
            lines = file.readlines()
        return {int(splitted[0]):splitted[1] for splitted in [line.split() for line in lines]  }
    
    def Detect(self, image:np.ndarray) -> list[Detection]:
        
        preparedImage = self.imagePreparation.Prepare(image,self.modelDetails)
        
        self.interpreter.set_tensor(self.modelDetails.InputTensorIndex, preparedImage)
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
