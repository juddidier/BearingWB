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
import FreeCADGui as Gui
import BearUtils
from BearUtils import _iconPath
import BearBase
import time

class bearModifierCmdList:
    def __init__(self):
        self.commands = {}

    def append(self, cmd, group = "modifier"):
        if not (group in self.commands):
            self.commands[group] = []
        self.commands[group].append(cmd)

    def getCommands(self, group):
        cmdList = []

        for cmd in self.commands[group]:
            cmdList.append(cmd)
        return cmdList

bearModifierCmd = bearModifierCmdList()

def bearGetModifierCmds():
    return bearModifierCmd.getCommands("modifier")


#****************************************************************************

class bearItemCmd:
    def __init__(self, type, help):
        self._type = type
        self._help = help

    def GetResources(self):
        return {'Pixmap': os.path.join(_iconPath, 'Bear'+self._type+'.svg'),
                'MenuText': "Add "+ self._help,
                'ToolTip': self._help}

    def Activated(self):
#        FreeCAD.Console.PrintMessage("bearCmd.Activated() ")
        start = int(time.time() * 1000)
        for selObj in BearUtils.bearGetAttachableSelections():
#            FreeCAD.Console.PrintMessage(selObj)
#            FreeCAD.Console.PrintMessage("    ")
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "bear" + self._type)
            BearBase.bearBaseObject(a, self._type, selObj)
            a.Label = self._type
            BearBase.bearViewProvider(a.ViewObject)
#        FreeCAD.Console.PrintMessage("\n")
        mid = int(time.time() * 1000)
        FreeCAD.ActiveDocument.recompute()
        end = int(time.time() * 1000)
        FreeCAD.Console.PrintMessage("execution: " + str(mid - start) + " - " + str(end - start) + " ms\n")
        return

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


#****************************************************************************

class BearFlip:
    def GetResources(self):
        return {'Pixmap': os.path.join(_iconPath, 'IconFlip.svg'),
                'MenuText': 'Flip Bearing',
                'ToolTip': 'Flip the Bearing so the anchor-point is on the opposite side'}

    def IsActive(self):
        selObjs = self.GetSelection()
        return len(selObjs) > 0
#        if not FreeCAD.ActiveDocument:
#            return False
#        return True

    def Activated(self):
        selObjs = self.GetSelection()
        if len(selObjs) == 0:
            return
        for selObj in selObjs:
            selObj.invert = not selObj.invert
        FreeCAD.ActiveDocument.recompute()
        return
#        FreeCAD.Console.PrintMessage("Flip Bearing\n")

    def GetSelection(self):
        bearObj = []
        for selObj in Gui.Selection.getSelectionEx():
            obj = selObj.Object
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, BearBase.bearBaseObject):
                if obj.baseObject is not None:
                    bearObj.append(obj)
        return bearObj

Gui.addCommand("BearFlip", BearFlip())
bearModifierCmd.append("BearFlip")


class BearMove:
    def GetResources(self):
        return {'Pixmap': os.path.join(_iconPath, 'IconMove.svg'),
                'MenuText': 'Move Bearing',
                'ToolTip': 'Move Bearing to another position'}

    def IsActive(self):
        selObj = self.GetSelection()
        if selObj[0] is not None:
            return True
        return False
#        if not FreeCAD.ActiveDocument:
#            return False
#        return True

    def Activated(self):
        selObj = self.GetSelection()
        if selObj[0] is None:
            return
        selObj[0].baseObject = selObj[1]
        FreeCAD.ActiveDocument.recompute()
        return
#        FreeCAD.Console.PrintMessage("Move Bearing\n")

    def GetSelection(self):
        bearObj = None
        edgeObj = None
        for selObj in Gui.Selection.getSelectionEx():
            obj = selObj.Object
            if hasattr(obj, 'Proxy') and isinstance(obj.Proxy, BearBase.bearBaseObject):
                bearObj = obj
        aselects = BearUtils.bearGetAttachableSelections()
        if len(aselects) > 0:
            edgeObj = aselects[0]
        return bearObj, edgeObj

Gui.addCommand("BearMove", BearMove())
bearModifierCmd.append("BearMove")


class BearSimplify:
    def GetResources(self):
        return {'Pixmap': os.path.join(_iconPath, 'IconSimplify.svg'),
                'MenuText': 'Simplify Bearing',
                'ToolTip': 'Convert Bearing to non-paramteric part'}

    def IsActive(self):
        return False
#        if not FreeCAD.ActiveDocument:
#            return False
#        return True

    def Activated(self):
        FreeCAD.Console.PrintMessage("Simplify Bearing\n")

Gui.addCommand("BearSimplify", BearSimplify())
bearModifierCmd.append("BearSimplify")
