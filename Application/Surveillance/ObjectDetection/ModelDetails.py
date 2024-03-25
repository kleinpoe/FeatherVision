from dataclasses import dataclass


@dataclass
class ModelDetails:
    IsFloatingPointModel:bool
    InputImageSize:tuple[int,int]
    InputTensorIndex:int