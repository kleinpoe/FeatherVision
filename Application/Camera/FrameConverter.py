import cv2
import numpy as np

from Config.Config import Config


class PreviewFrameToRgbConverter:
    def __init__(self, config: Config):
        self.resolution = config.Camera.ObjectDetectionResolution
    
    def ConvertToRgb(self, frame:np.ndarray) -> np.ndarray:
        return cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)[:,:self.resolution[0],:]