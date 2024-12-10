from marshmallow_dataclass import dataclass

from model.Obstacle import Obstacle
from model.Point2D import Point2D
from model.Point import Point


@dataclass
class Panel:
    id: str = None

    width: float = None
    height: float = None

    xLeft: float = None
    xRight: float = None
    yBottom: float = None
    yTop: float = None

    shape: str = None
    isI2bottom: bool = False

    gap: float = 0
    gapBottom: float = 0
    gapTop: float = 0

    center2D: Point2D = Point2D()
    center3D: Point = Point()

    obstacleOnLeft: bool = False
    obstacleOnRight: bool = False
    obstacleOnTop: bool = False
    obstacleOnBottom: bool = False
    obstacle: Obstacle = None

    # def __init__(
    #     self,
    #     id: str,
    #     xLeft: float,
    #     xRight: float,
    #     obstacles: [Obstacle],
    #     width: float = STANDARD_PANEL_WIDTH,
    #     height: float = STANDARD_PANEL_HEIGHT,
    #     isI2bottom: bool = False,
    # ):
    #     self.id = id
    #     self.xLeft = xLeft
    #     self.xRight = xRight
    #     self.width = width
    #     self.height = height
    #     self.isI2bottom = isI2bottom
    #     self._setPrivateProperties(obstacles)
    #     xCenter = (self.xLeft + self.xRight) / 2
    #     yCenter = (self.yBottom + self.yTop) / 2
    #     self.center2D = Point2D(xCenter, yCenter)

    def update_from_dict(self, obstacles: [Obstacle]):
        self._setObstaclesBoundaries(obstacles)
        self._setShape()
        self._setGaps()
        self._setY()
        self._setHeights()
        self._setCenter()

    def _setObstaclesBoundaries(self, listObstacles: [Obstacle]):
        for i in range(0, len(listObstacles)):
            # If the Obstacle touches the left edge of the Panel...
            if (
                listObstacles[i].xLeft < self.xLeft
                and listObstacles[i].xRight > self.xLeft
            ):
                # ... add the Obstacle to the Panel's property and set the obstacleOnLeft propety to True.
                self.obstacleOnLeft = True
                self.obstacle = listObstacles[i]

            # If the Obstacle touches the right edge of the Panel...
            if (
                listObstacles[i].xLeft < self.xRight
                and listObstacles[i].xRight > self.xRight
            ):
                # ... add the Obstacle to the Panel's property and set the obstacleOnRight property to True.
                self.obstacleOnRight = True
                self.obstacle = listObstacles[i]
            # If the Obstacle touches the top of the Panel, set the obstacleOnTop property to True.
            if (self.obstacleOnLeft or self.obstacleOnRight) and listObstacles[
                i
            ].topDistanceFromTopWall <= 0:
                self.obstacleOnTop = True
            # If the Obstacle touches the bottom of the Panel, set the obstacleOnBottom property to True.
            elif (self.obstacleOnLeft or self.obstacleOnRight) and listObstacles[
                i
            ].yBottom <= 0:
                self.obstacleOnBottom = True

        return self

    def _setShape(self):
        # Si l'obstacle touche les deux cotés...
        if self.obstacleOnLeft and self.obstacleOnRight:
            # ... et le haut du mur => I 1 bottom
            if self.obstacleOnTop:
                self.shape = "i1b"
            # ... et le bas du mur => I 1 top
            elif self.obstacleOnBottom:
                self.shape = "i1t"
            # ... mais pas le haut ou le bas du mur => I 2 Bottom + I 2 Top
            else:
                self.shape = "i2"

        # Si l'obstacle touche sur le coté gauche...
        elif self.obstacleOnLeft:
            # ... et le haut => L bottom right
            if self.obstacleOnTop:
                self.shape = "lbr"
            # ... et le bas => L top right
            elif self.obstacleOnBottom:
                self.shape = "ltr"
            # ... mais pas le haut ou le bas du mur => C Right
            else:
                self.shape = "cr"

        # Si l'obstacle touche sur le coté droit
        elif self.obstacleOnRight:
            # ... et le haut => L bottom left
            if self.obstacleOnTop:
                self.shape = "lbl"
            # ... et le bas => L top left
            elif self.obstacleOnBottom:
                self.shape = "ltl"
            # ... mais pas le haut ou le bas du mur => C Left
            else:
                self.shape = "cl"
        else:
            self.shape = "i"

        return self

    def _setGaps(self):
        # Set gap for Left side Panels
        if self.shape == "cl" or self.shape == "lbl" or self.shape == "ltl":
            self.gap = self.obstacle.xLeft - self.xLeft
        # Set gap for Right side Panels
        if self.shape == "cr" or self.shape == "lbr" or self.shape == "ltr":
            self.gap = self.xRight - self.obstacle.xRight
        # Set gapBottom for C and L bottom shapes Panels
        if (
            self.shape == "cl"
            or self.shape == "cr"
            or self.shape == "lbl"
            or self.shape == "lbr"
        ):
            self.gapBottom = self.obstacle.yBottom
        # Set gapTop for C and L top shapes Panels
        if (
            self.shape == "cl"
            or self.shape == "cr"
            or self.shape == "ltl"
            or self.shape == "ltr"
        ):
            self.gapTop = self.height - self.obstacle.yTop

        return self

    def _setHeights(self):
        if self.shape == "i2" or self.shape == "i1t" or self.shape == "i1b":
            if self.shape != "i2":
                self.height = self.height - self.obstacle.height
            else:
                if self.isI2bottom:
                    self.height = self.obstacle.yBottom
                else:
                    self.height = self.height - self.obstacle.yTop

    def _setY(self):
        if self.shape == "i2" or self.shape == "i1t" or self.shape == "i1b":
            if self.shape == "i1t":
                self.yTop = self.height
                self.yBottom = self.obstacle.yTop
            if self.shape == "i1b":
                self.yTop = self.obstacle.yBottom
                self.yBottom = 0
            if self.shape == "i2":
                if self.isI2bottom:
                    self.yTop = self.obstacle.yBottom
                    self.yBottom = 0
                else:
                    self.yTop = self.height
                    self.yBottom = self.obstacle.yTop
        else:
            self.yBottom = 0
            self.yTop = self.height

    def _setCenter(self):
        xCenter = (self.xLeft + self.xRight) / 2
        yCenter = (self.yBottom + self.yTop) / 2
        self.center2D = Point2D(xCenter, yCenter)
