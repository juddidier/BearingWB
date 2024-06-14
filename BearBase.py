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

import os
import FreeCAD
import BearUtils
import math
import DraftVecUtils
from BearMaker import bearMaker
from BearUtils import _iconPath


class bearBaseObject:
    propertyChange = ''
    backup = {'type':''}

    def __init__(self, obj, type, attachTo):
#        FreeCAD.Console.PrintMessage("bearBaseObject.__init__\n")
        obj.addProperty("App::PropertyDistance", "offset", "Parameters", "Offset from surface").offset = 0.0
        obj.addProperty("App::PropertyBool", "invert", "Parameters", "Invert bearing direction").invert = False
        obj.addProperty("App::PropertyXLinkSub", "baseObject", "Parameters", "Base object").baseObject = attachTo

        #*** add compatible bearings (aka same family) ***
        famItems = BearUtils.bearFamilies[BearUtils.bearItemsTable[type][1]]['items']
        obj.addProperty("App::PropertyEnumeration", 'type', 'Parameters', 'Bearing type').type = famItems
        obj.type = type

        #*** add sizes accroding the Bearing type ***
        sizeCodes = bearMaker.getAllSizeCodes(type)
        obj.addProperty("App::PropertyEnumeration", 'sizeCode', 'Parameters', 'Bearing Size').sizeCode = sizeCodes
        obj.sizeCode = sizeCodes[0]

        #*** add Family-Properties ***
        self.backup['type'] = type
        self.addFamilyProperties(obj)
        obj.Proxy = self

    def onBeforeChange(self, obj, prop):
#        FreeCAD.Console.PrintMessage("onBeforeChange: " + self.propertyChange + "\n")
        self.propertyChange = prop
#        FreeCAD.Console.PrintMessage("modified: " + prop + "  old Val: " + str(getattr(obj, prop)) + "\n")

    def execute(self, fp):
#        FreeCAD.Console.PrintMessage("execute\n")
        try:
            shape = fp.baseObject[0].Shape.getElement(fp.baseObject[1][0])
        except:
            shape = None

        if 'type' in self.propertyChange:
            sizeCodes = bearMaker.getAllSizeCodes(fp.type)
            fp.sizeCode = sizeCodes
            fp.sizeCode = sizeCodes[0]

        if 'type' in self.propertyChange or 'sizeCode' in self.propertyChange:
            self.addFamilyProperties(fp)

        self.propertyChange = ''
        self.backupProperties(fp)
#        FreeCAD.Console.PrintMessage("execute(): ")
#        FreeCAD.Console.PrintMessage(self.backup)
#        FreeCAD.Console.PrintMessage("\n")

        shp = bearMaker.createBearing(fp)
        fp.Shape = shp

        fp.Label2 = fp.sizeCode + self.getFamilyPropSuffix(fp)

        if shape is not None:
            bearMoveToObject(fp, shape)

    def addFamilyProperties(self, obj):
        if self.backup['type'] != '':
            for prop in BearUtils.bearItemsTable[self.backup['type']][2]:
                obj.removeProperty(prop)
        for prop, propType in BearUtils.bearItemsTable[obj.type][2].items():
            propContent = bearMaker.getParamItems(obj.type, prop, propType, obj.sizeCode)
            obj.addProperty("App::Property" + propType, prop, 'Parameters', prop)
            setattr(obj, prop, propContent)
#            FreeCAD.Console.PrintMessage("addFamProp() prop:" + str(prop) + " - self.backup: " + str(self.backup) + " - propContent: " + str(propContent) + "\n")
            if prop in self.backup:# and self.backup[prop] in propContent:
#                FreeCAD.Console.PrintMessage("prop in self.backup\n")
                if propType == 'Enumeration':
#                    FreeCAD.Console.PrintMessage("propType is Enum\n")
                    if self.backup[prop] in propContent:
#                        FreeCAD.Console.PrintMessage("self.backup[prop] in propContent\n")
                        setattr(obj, prop, self.backup[prop])
                else:
#                    FreeCAD.Console.PrintMessage("propType is NOT Enum\n")
                    setattr(obj, prop, self.backup[prop])

    def getFamilyPropSuffix(Self, obj):
        propContent = ""
        for prop, propType in BearUtils.bearItemsTable[obj.type][2].items():
            suffix = str(getattr(obj, prop))
            if suffix != "-":
                propContent += " " + suffix
        return propContent

    def backupProperties(self, obj):
        self.backup.clear()
        self.backup['type'] = obj.type
        self.backup['sizeCode'] = obj.sizeCode

        for prop in BearUtils.bearItemsTable[obj.type][2]:
#            FreeCAD.Console.PrintMessage("backupProperties(): " + str(prop) + "\n")
            self.backup[prop] = getattr(obj, prop) #bearMaker.getParamItems(obj.type, prop, propType, obj.sizeCode)


#****************************************************************************

class bearViewProvider:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        self.Object = obj.Object
        return

    def updateData(self, fp, prop):
        return

    def getDisplayModes(self, obj):
        return []

#    def getDefaultDisplayMode(self):
#        return 'Shaded'

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
#        FreeCAD.Console.PrintMessage("Prop changed: " + str(prop) + "\n")
        return

    def getIcon(self):
        if hasattr(self.Object, 'type'):
            return os.path.join(_iconPath, "Bear" + self.Object.type + '.svg')
#        elif hasattr(self.Object.Proxy, 'type'):
#            return os.path.join(_iconPath, self.Object.Proxy.type + '.svg')
        return os.path.join(_iconPath, 'BearingLogo.svg')

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        if state is not None:
            self.Object = FreeCAD.ActiveDocument.getObject(state['ObjectName'])
#        return None


def bearMoveToObject(bearObj, attachToObj):
    ptn1 = None
    axis1 = None
    axis2 = None
    if hasattr(attachToObj, 'Curve'):
        if hasattr(attachToObj.Curve, 'Center'):
            pnt1 = attachToObj.Curve.Center
            axis1 = attachToObj.Curve.Axis
    if hasattr(attachToObj, 'Surface'):
        if hasattr(attachToObj.Surface, 'Axis'):
            axis1 = attachToObj.Surface.Axis

    if hasattr(attachToObj, 'Point'):
        pnt1 = attachToObj.Point

    if axis1 is not None:
        if bearObj.invert:
            axis1 = FreeCAD.Base.Vector(0, 0, 0) - axis1

        pnt1 = pnt1 + axis1 * bearObj.offset.Value
        axis2 = FreeCAD.Base.Vector(0.0, 0.0, 1.0)
        axis2Minus = FreeCAD.Base.Vector(0.0, 0.0, -1.0)

        if axis1 == axis2:
            normvec = FreeCAD.Base.Vector(1.0, 0.0, 0.0)
            result = 0.0
        else:
            if axis1 == axis2Minus:
                normvec = FreeCAD.Base.Vector(1.0, 0.0, 0.0)
                result = math.pi
            else:
                normvec = axis1.cross(axis2)
                normvec.normalize()
                result = DraftVecUtils.angle(axis1, axis2, normvec)

        normvec.multiply(-math.sin(result / 2))
        pl = FreeCAD.Placement()
        pl.Rotation = (normvec.x, normvec.y, normvec.z, math.cos(result / 2))

        bearObj.Placement = FreeCAD.Placement()
        bearObj.Placement.Rotation = pl.Rotation.multiply(bearObj.Placement.Rotation)
        bearObj.Placement.move(pnt1)
