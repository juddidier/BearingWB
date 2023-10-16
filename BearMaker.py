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
import importlib
from pathlib import Path
from BearUtils import _dataPath
from BearUtils import csv2dict
from BearUtils import bearItemsTable

class bearMakerClass():
    bearData = {}
    bearTitles = {}
    fileList = {}

    def __init__(self):
        self.objAvailable = True
        self.fileList = Path(_dataPath).glob('*.csv')

        for file in self.fileList:
            tables = csv2dict(str(file), file.stem, fieldNamed=True)
            for tableName in tables.keys():
                if tableName == 'titles':
                    self.bearTitles.update(tables[tableName])
                else:
                    self.bearData[tableName] = tables[tableName]

    def getAllSizeCodes(self, type):
        return list(self.bearData[type + '_def'].keys())

    def getParamItems(self, type, prop, propType, sizeCode):
        typekey = type + '_' + prop
#        FreeCAD.Console.PrintMessage(typekey + "\n")
        if propType == 'Enumeration' and typekey in self.bearData:
#            FreeCAD.Console.PrintMessage("Enum & key exist\n")
            return self.bearData[typekey][sizeCode]
        else:
            return None

    def createBearing(self, fp):
        function = bearItemsTable[fp.type][3]

        try:
            if not hasattr(self, function):
                setattr(bearMakerClass, function, getattr(importlib.import_module("BearFunctions.bear"+function), function))
        except ValueError:
            FreeCAD.Console.PrintMessage("Error! loading custom Bearing function!\n")

        if function != '':
            function = "self." + function + "(fp)"
            bearShape = eval(function)

        return bearShape


bearMaker = bearMakerClass()