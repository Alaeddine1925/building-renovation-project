from typing import List
from marshmallow_dataclass import dataclass
from dataclasses import field

import math
import pandas as pd

from model.Wall import Wall
from model.BeamAssembly import BeamAssembly
from model.Beam import Beam
from model.Panel import Panel
from model.Clip import Clip
from model.Point2D import Point2D
from model.Point import Point


@dataclass
class BillOfMaterials:
    id: str = None
    version: str = "VK02"
    useLegs: bool = False
    doubleBeams: bool = False
    panels: List[Panel] = field(default_factory=list)
    standardPanelsCount: int = 0
    customPanelsCount: int = 0
    beams: List[Beam] = field(default_factory=list)
    standardBeamsCount: int = 0
    customBeamCount: int = 0
    screwsCount: int = 0
    legsCount: int = 0
    panelScrewsCount: int = 0
    iClips: List[Clip] = field(default_factory=list)
    iClipsCount: int = 0
    jsonBeamsDataFrame: str = None
    jsonPanelsDataFrame: str = None

    def __init__(self, wall: Wall):
        self.screwsCount = self._setScrews(wall.beamAssemblies)
        self.panelScrewsCount = self._setPanelScrews(wall.beamAssemblies)
        self.legsCount = self._setLegs(wall.beamAssemblies)
        self.panels = wall.panels
        self.beams = self._getAllBeams(wall.beamAssemblies)
        panels = self._setPanels(wall.panels)
        self.standardPanelsCount = panels[0]
        self.customPanelsCount = panels[1]
        self.useLegs = False
        self.version = "VK02"
        self.jsonBeamsDataFrame = self._getBeamsDataFrame().to_json()
        self.jsonPanelsDataFrame = self._getPanelsDataFrame().to_json()
        self.iClips = []
        self.iClipsCount = self._setIClips(wall)

    def _addExtraElem(self, length, step):
        remainingLength = length - step
        if remainingLength > 0:
            return 1 + int(remainingLength / step)
        return 0

    def _setScrews(self, beamAssemblies: [BeamAssembly]):
        screwsCount = 0
        # Iterate over the beams and add 2 screws to the WonderCart for each beam
        # plus an extra screw for beams longer than 60cm every extra 60cm.

        for beamAssembly in beamAssemblies:
            for beam in beamAssembly.beamList:
                length = beam.length
                screwsCount = screwsCount + 2 + self._addExtraElem(length, 0.6)
        return screwsCount

    def _setLegs(self, beamAssemblies: [BeamAssembly]):
        # Given the first element of beamsList being the horizontal beams on the bottom of the wall,
        # add 1 leg for every 60cm of beam with a minimum of 1 per beam.
        bottomWallBeams = []
        for beamAssembly in beamAssemblies:
            if beamAssembly.category == "bottomWallBeams":
                bottomWallBeams.append(beamAssembly)
        # TODO: implement the algo with new getBeams API call result
        wallLength = 0
        # beams = resultBeams["bottomWallBeams"]
        for beamAssembly in bottomWallBeams:
            for beam in beamAssembly.beamList:
                wallLength = wallLength + beam.length
        legs = math.ceil(wallLength / 0.6)
        return legs if legs > len(bottomWallBeams) else len(bottomWallBeams)

    def _setPanelScrews(self, beamAssemblies: [BeamAssembly]):
        panelScrewsCount = 0
        # Add 2 panelScrews per vertical beams plus an additional panelScrew every 60cm of beam.
        for beamAssembly in beamAssemblies:
            for beam in beamAssembly.beamList:
                if beam.orientation == "Vertical":
                    panelScrewsCount = (
                        panelScrewsCount + 2 + self._addExtraElem(beam.length, 0.6)
                    )
        return panelScrewsCount

    # WIP
    def _setPanels(self, panels: [Panel]):
        standardPanels = []
        customPanels = []
        for panel in panels:
            if panel.shape == "i" and panel.width > 0.59:
                standardPanels.append(panel)
            else:
                customPanels.append(panel)
        return [len(standardPanels), len(customPanels)]

    def _getAllBeams(self, beamAssemblies):
        beams = []
        standardBeams = []
        customBeams = []
        for beamAssembly in beamAssemblies:
            for beam in beamAssembly.beamList:
                if beam.length == 1.8:
                    standardBeams.append(beam)
                else:
                    customBeams.append(beam)
                beams.append(beam)
        return beams

    def _getPanelsDataFrame(self):
        df = pd.DataFrame(self.panels)
        df["width2"] = df["width"].apply(lambda x: str(round(x, 2)))
        df["height2"] = df["height"].apply(lambda x: str(round(x, 2)))
        df["gap2"] = df["gap"].apply(lambda x: str(round(x, 2)))
        df["gapBottom2"] = df["gapBottom"].apply(lambda x: str(round(x, 2)))
        df["gapTop2"] = df["gapTop"].apply(lambda x: str(round(x, 2)))
        df["b"] = 1

        a = pd.pivot_table(
            df,
            values="width",
            index=["shape", "width2", "height2", "gap2", "gapBottom2", "gapTop2"],
            columns="b",
            aggfunc="count",
        )

        return a

    def _getBeamsDataFrame(self):
        df = pd.DataFrame(self.beams)
        df["length2"] = df["length"].apply(lambda x: str(x))
        df["b"] = 1
        # df.to_csv("file1.csv")
        a = pd.pivot_table(
            df, values="length", index="length2", columns="b", aggfunc="count"
        )
        return a

    # TODO: Clips?
    def _setIClips(self, wall):
        iClipsCount = 0
        # Iterate over the beams and compare each pair of consecutive beams...
        for beamAssembly in wall.beamAssemblies:
            for first_beam, second_beam in zip(
                beamAssembly.beamList, beamAssembly.beamList[1:]
            ):
                # ... If they are touching each other, add a clipsI to the WonderCart.
                if (
                    first_beam.orientation == "Horizontal"
                    and first_beam.xRight == second_beam.xLeft
                ) or (
                    first_beam.orientation == "Vertical"
                    and first_beam.yTop == second_beam.yBottom
                ):
                    iClipsCount = iClipsCount + 2
                    point2D = Point2D(
                        first_beam.wallFixations[-1].x, first_beam.wallFixations[-1].y
                    )
                    iClip = Clip(center2D=point2D, orientation=first_beam.orientation)
                    iClip.center3D = wall.set3DCenterForChild(iClip)
                    self.iClips.append(iClip)
                    # print(f"{first_beam['name']} and {second_beam['name']} are connected.")
                # else:
                #     print(
                #         f"{first_beam['name']} and {second_beam['name']} are NOT connected."
                #     )
        return iClipsCount
