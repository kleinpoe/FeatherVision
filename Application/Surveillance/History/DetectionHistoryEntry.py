from datetime import datetime
from Surveillance.ObjectDetection.Detection import Detection

import numpy as np

from dataclasses import dataclass

@dataclass
class DetectionHistoryEntry:
    Detections: list[Detection]
    Timestamp: datetime
    Frame: np.ndarray

    def __repr__(self) -> str:
        formattedDetections = ' '.join([f'{x.Label}({x.Score*100:.0f}%)' for x in self.Detections])
        formattedTimestamp = self.Timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f'<Entry {formattedTimestamp} Detections=[ {formattedDetections} ]>'