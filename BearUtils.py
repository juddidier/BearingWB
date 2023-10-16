# -*- coding: utf-8 -*-
# ***************************************************************************
# *   (c) Didier Jud 2023                                                   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD
import FreeCADGui as Gui
import Part
import os
import csv
import math
from pathlib import Path


_dir = os.path.dirname(__file__)
_iconPath = os.path.join(_dir, 'Icons')
_dataPath = os.path.join(_dir, 'Data')

noneParams = {}
baseAxialParams = {'shield':'Enumeration'}

bearFamilies = {
    'AxialFamily': {'desc': "axial Bearings",},
#    'RadialFamily': {'desc': "radial Bearings",},
}

bearItemsTable = {
    "MRxxx": ("MR-type metric small axial bearing", 'AxialFamily', baseAxialParams, 'MakeBaseAxialBearing'),
    "6xx": ("600-type metric small axial bearing", 'AxialFamily', baseAxialParams, 'MakeBaseAxialBearing'),
}

for item in bearItemsTable:
    famName = bearItemsTable[item][1]
    if famName in bearFamilies:
        if not ('items' in bearFamilies[famName]):
            bearFamilies[famName]['items'] = []
        bearFamilies[famName]['items'].append(str(item))


#****************************************************************************

def bearGetAttachableSelections():
    def positionDone(center, radius, doneList, tol=1e-6):
        for itm in doneList:
            if center.isEqual(itm[0], tol) and math.isclose(radius, itm[1], tol):
                return True
        return False

    def getEdgeName(obj, edge):
        i = 1
        for e in obj.Edges:
            if e.isSame(edge):
                return 'Edge' + str(i)
            i += 1
        return None

    asels = []
    for selObj in Gui.Selection.getSelectionEx():
        baseObjectNames = selObj.SubElementNames
        obj = selObj.Object
        grp = obj.getParentGeoFeatureGroup()
        if grp is not None and hasattr(grp, 'TypeId') and grp.TypeId == "PartDesign::Body":
            obj = grp

        posDoneList = []

        for bObjN in baseObjectNames:
            shape = obj.Shape.getElement(bObjN)

            if hasattr(shape, 'Curve'):
                if not hasattr(shape.Curve, 'Center'):
                    continue
                if not hasattr(shape.Curve, 'Radius'):
                    continue
                if positionDone(shape.Curve.Center, shape.Curve.Radius, posDoneList):
                    continue
                asels.append((obj, [bObjN]))
                posDoneList.append([shape.Curve.Center, shape.Curve.Radius])
#                FreeCAD.Console.PrintMessage("Linking to " + obj.Name + "[" + bObjN + "]\n")

            elif isinstance(shape, Part.Face):
                outerEdgeList = shape.OuterWire.Edges
                for edge in shape.Edges:
                    if not hasattr(edge, 'Curve'):
                        continue
                    if not hasattr(edge.Curve, 'Center'):
                        continue
                    if not hasattr(edge.Curve, 'Radius'):
                        continue
                    if positionDone(edge.Curve.Center, edge.Curve.Radius, posDoneList):
                        continue
                    for outerEdge in outerEdgeList:
                        if outerEdge.isSame(edge):
                            edge = None
                            break
                    if edge is None:
                        continue
                    edgeName = getEdgeName(obj.Shape, edge)
                    if edgeName is None:
                        continue
                    asels.append((obj, [edgeName]))
                    posDoneList.append([edge.Curve.Center, edge.Curve.Radius])
#                    FreeCAD.Console.PrintMessage("Linking to " + "[" + edgeName + "[\n")

    if len(asels) == 0:
        asels.append(None)
    return asels


def csv2dict(fileName, defTableName, fieldNamed = True):
    with open(fileName) as fp:
        reader = csv.reader(fp, skipinitialspace=True, dialect='unix', quoting=csv.QUOTE_NONNUMERIC,)
        tables = {}
        tables['titles'] = {}
        newTable = False
        firstTable = True
        curTable = {}
        tableNames = {defTableName}

        for lineList in reader:
            if len(lineList) == 0:
                continue
            elif len(lineList) == 1:
                tblName = lineList[0]
                if not newTable:
                    curTable = {}
                    tableNames = set()
                    newTable = True
                tableNames.add(tblName)
                continue
            key = lineList[0]
            data = tuple(lineList[1:])
            if newTable or firstTable:
                firstTable = False
                newTable = False
                for tblName in tableNames:
                    tables[tblName] = curTable
                if fieldNamed:
                    for tblName in tableNames:
                        tables['titles'][tblName] = data
                    continue
            curTable[key] = data
#        FreeCAD.Console.PrintMessage(tables)
#        FreeCAD.Console.PrintMessage("\n")

        return tables


#****************************************************************************

class bearFaceMaker:

    def __init__(self):
        self.reset()

    def reset(self):
        self.edges = []
        self.firstPoint = None

    def addPoint(self, x, z):
        curPoint = FreeCAD.Base.Vector(x, 0, z)
        if self.firstPoint is None:
            self.firstPoint = curPoint
        else:
            self.edges.append(Part.makeLine(self.lastPoint, curPoint))
        self.lastPoint = curPoint

    def addPoints(self, *args):
        for arg in args:
#            FreeCAD.Console.PrintMessage(arg)
#            FreeCAD.Console.PrintMessage("\n")
            if len(arg) == 2:
                self.addPoint(arg[0], arg[1])

    def startPoint(self, x, z):
        self.reset()
        self.addPoint(x, z)

    def addArc(self, x1, z1, x2, z2):
        midPoint = FreeCAD.Base.Vector(x1, 0, z1)
        endPoint = FreeCAD.Base.Vector(x2, 0, z2)
        self.edges.append(Part.Arc(self.lastPoint, midPoint, endPoint).toShape())
        self.lastPoint = endPoint

    def addArc2(self, xc, zc, a):
        a = math.radians(a)
        xac = self.lastPoint.x + xc
        zac = self.lastPoint.z + zc
        sa = math.atan2(-zc, -xc)
        r = math.sqrt(xc * xc + zc * zc)
        sa += a / 2.0
        x1 = xac + r * math.cos(sa)
        z1 = zac + r * math.sin(sa)
        sa += a / 2.0
        x2 = xac + r * math.cos(sa)
        z2 = zac + r * math.sin(sa)
        self.addArc(x1, z1, x2, z2)

    def getClosedWire(self):
        self.edges.append(Part.makeLine(self.lastPoint, self.firstPoint))
        return Part.Wire(self.edges)

    def getFace(self):
        return Part.Face(self.getClosedWire())

    def revolveZ(self, profile: Part.Shape) -> Part.Shape:
        return profile.revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)

#****************************************************************************

bearData = {}
bearTitles = {}
fileList = Path(_dataPath).glob("*.csv")
for file in fileList:
    tables = csv2dict(str(file), file.stem, True)
    for tableName in tables.keys():
        if tableName == 'titles':
            bearTitles.update(tables[tableName])
        else:
            bearData[tableName] = tables[tableName]
