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
from BearMaker import bearMaker
from BearUtils import _iconPath


class bearBaseObject:
    propertyChange = ''
    oldType = ''

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
#        sizeCodes = ["aa","bb","cc"]
        obj.addProperty("App::PropertyEnumeration", 'sizeCode', 'Parameters', 'Bearing Size').sizeCode = sizeCodes
        obj.sizeCode = sizeCodes[0]

        #*** add Family-Properties ***
        self.addFamilyProperties(obj)
        self.oldType = type
        obj.Proxy = self

    def onBeforeChange(self, obj, prop):
        self.propertyChange += prop +' '
#        FreeCAD.Console.PrintMessage("onBeforeChange: " + self.propertyChange + "\n")

    def execute(self, fp):
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

        fp.Label = fp.sizeCode + self.getFamilyPropSuffix(fp)

        self.propertyChange = ''
        self.oldType = fp.type

        shape = bearMaker.createBearing(fp)
        fp.Shape = shape


    def addFamilyProperties(self, obj):
        if self.oldType != '':
            for prop in BearUtils.bearItemsTable[self.oldType][2]:
                obj.removeProperty(prop)
        for prop, propType in BearUtils.bearItemsTable[obj.type][2].items():
            propContent = bearMaker.getParamItems(obj.type, prop, propType, obj.sizeCode)
            if not hasattr(obj, prop):
                obj.addProperty("App::Property" + propType, prop, 'Parameters', prop)
                setattr(obj, prop, propContent)

    def getFamilyPropSuffix(Self, obj):
        propContent = ""
        for prop, propType in BearUtils.bearItemsTable[obj.type][2].items():
            suffix = str(getattr(obj, prop))
            if suffix != "-"
                propContent += " " + suffix
        return propContent

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

    def getDefaultDisplayMode(self):
        return 'Shaded'

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
        return None