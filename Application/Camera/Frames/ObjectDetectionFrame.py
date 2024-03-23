import numpy as np

from dataclasses import dataclass
from datetime import datetime

@dataclass
class ObjectDetectionFrame:
    Frame:np.ndarray
    Timestamp:datetime