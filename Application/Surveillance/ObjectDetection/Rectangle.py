from dataclasses import dataclass


@dataclass
class Rectangle:
    Position:tuple[float,float]
    Size:tuple[float,float]
    @property
    def Width(self)->float:
        return self.Size[0]
    @property
    def Height(self)->float:
        return self.Size[1]
    @property
    def Top(self)->float:
        return self.Position[0]
    @property
    def Left(self)->float:
        return self.Position[1]
    @property
    def Bottom(self)->float:
        return self.Position[0] + self.Size[0]
    @property
    def Right(self)->float:
        return self.Position[1] + self.Size[1]
    @classmethod
    def FromPadding(cl, topLeftBottomRight:tuple[float,float,float,float]) -> 'Rectangle':
        top, left, bottom, right = topLeftBottomRight
        actualLeft = min(left,right)
        actualRight = max(left,right)
        actualTop = min(top,bottom)
        actualBottom = max(top,bottom)
        return Rectangle(Position=(actualTop,actualLeft), Size=(actualBottom-actualTop, actualRight-actualLeft))
    
    @classmethod
    def Average(cl, rectangle1: 'Rectangle', rectangle2: 'Rectangle'):
        return Rectangle.FromPadding(((rectangle1.Top + rectangle2.Top)/2.0,(rectangle1.Left + rectangle2.Left)/2.0, (rectangle1.Bottom + rectangle2.Bottom)/2.0, (rectangle1.Right + rectangle2.Right)/2.0 ))