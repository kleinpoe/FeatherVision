from Application.Config.Config import Config
from Application.Surveillance.ObjectDetection.Detection import Detection


from typing import Callable


class DetectionBroadcaster:
    def __init__(self, broadcastDetections: Callable[[list[Detection]],None], config: Config):
        self.broadcastDetections = broadcastDetections
        self.config = config

    def Broadcast(self, detections: list[Detection]):
        # filter more?
        resultsOverThresholdScore = [result for result in detections if result.Score > self.config.ClipGeneration.MinimumScore]
        self.broadcastDetections(resultsOverThresholdScore)