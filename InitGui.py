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

class BearingWorkbench(Workbench):
    import BearUtils

    MenuText = "Bearing"
    ToolTip = "Create standard Bearings"
    Icon = os.path.join(BearUtils._iconPath, "BearingLogo.svg")
    modifyCmds = []

    def Initialize(self):
        from BearUtils import bearFamilies as _bearFam
        from BearUtils import bearItemsTable as _bearItems
        import BearCmd
        FreeCAD.Console.PrintMessage("Initialize\n")

        self.modifyCmds = BearCmd.bearGetModifierCmds()
        self.appendToolbar("Bearing Modifiers", self.modifyCmds)
        self.appendMenu("Bearing", self.modifyCmds)

        for family in _bearFam:
            famItem = _bearFam[family]
            self.appendToolbar(famItem['desc'], famItem['items'])
            for bearItem in famItem['items']:
                Gui.addCommand(bearItem, BearCmd.bearItemCmd(bearItem, _bearItems[bearItem][0]))

    def Activated(self):
        pass

    def Deactivated(self):
        pass

    def ContextMenu(self, recipient):
        self.appendContextMenu("Bearing", self.modifyCmds)

    def GetClassName(self):
        return "Gui::PythonWorkbench"

Gui.addWorkbench(BearingWorkbench())
