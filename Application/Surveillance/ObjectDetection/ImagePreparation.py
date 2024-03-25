from Surveillance.ObjectDetection.ModelDetails import ModelDetails

import cv2
import numpy as np


class ImagePreparation:
    def Prepare(self, rgbArray:np.ndarray, modelDetails:ModelDetails) -> np.ndarray:
        resized = cv2.resize(rgbArray, modelDetails.InputImageSize)
        expanded = np.expand_dims(resized, axis=0)
        if modelDetails.IsFloatingPointModel:
            expanded = (np.float32(expanded) - 127.5) / 127.5 # Todo change to avg and scale with std
        return expanded