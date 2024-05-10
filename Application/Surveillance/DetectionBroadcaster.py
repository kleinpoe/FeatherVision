from Config.Config import Config
from Surveillance.ObjectDetection.Detection import Detection


from typing import Callable


class DetectionBroadcaster:
    def __init__(self, broadcastDetections: Callable[[list[Detection]],None], config: Config):
        self.broadcastDetections = broadcastDetections
        self.config = config

    def Broadcast(self, detections: list[Detection]):
        
        def isAboveThreshold(detection: Detection):
            return detection.Score > self.config.ClipGeneration.MinimumScoreForStream
        
        def isTracked(detection: Detection):
            return self.config.ClipGeneration.ShowAlsoUntrackedObjectsInStream or (detection.Label in self.config.ClipGeneration.TrackedObjectsLabels)
        
        filteredDetections = [result for result in detections if isAboveThreshold(result) and isTracked(result)]
        self.broadcastDetections(detections=filteredDetections)