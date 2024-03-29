from dataclasses import dataclass
from datetime import datetime

@dataclass
class HighResolutionFrame:
    Frame:bytes
    IsKeyframe:bool
    Timestamp:datetime
    RawTimestamp:int