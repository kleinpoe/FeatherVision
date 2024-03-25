from typing import Optional
from Surveillance.ObjectDetection.Rectangle import Rectangle
from dataclasses import dataclass


@dataclass
class Detection:
    BoundingBox:Rectangle
    Score:float
    LabelIndex:int
    Label:Optional[str]