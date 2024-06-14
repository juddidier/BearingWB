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
import Part
#import Draft
import math
from BearMaker import *
import BearUtils

def MakeRadialSphericalPlainBearing(self, fp):
#    FreeCAD.Console.PrintMessage("makeBaseAxialBearing()\n")

#    FreeCAD.Console.PrintMessage(fp.type)
#    FreeCAD.Console.PrintMessage(" - ")
#    FreeCAD.Console.PrintMessage(fp.sizeCode)
#    FreeCAD.Console.PrintMessage("\n")

    d, D, B, C, dk, r1, r2 = bearMaker.bearData[fp.type+"_def"][fp.sizeCode]
    r = d / 2
    R = D / 2
    B2 = B / 2
    C2 = C / 2
    rk = dk / 2
    rs = math.sqrt(rk*rk - B2*B2)
    rsC = math.sqrt(rk*rk - (C2-r1)*(C2-r1))

    fm = BearUtils.bearFaceMaker()
#    fm.addPoint(r, B2-r1)
#    fm.addArc2(r1, 0.0, -90)
#    fm.addPoint(rs, B2)
#    fm.addArc(rk, 0.0, rs, -B2)
#    fm.addPoint(r+r1, -B2)
#    fm.addArc2(0.0, r1, -90)
    fm.addPoint(r, B2+C2)
    fm.addPoint(rs, B2+C2)
    fm.addArc(rk, C2, rs, -B2+C2)
    fm.addPoint(r, -B2+C2)

#    shape1 = fm.getFace().revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)
    shape1 = fm.revolveZ(fm.getFace())

    fm.reset()
#    fm.addPoint(rsC, C2-r1)
#    fm.addArc2(r1, 0.0, -90)
#    fm.addPoint(R-r2, C2)
#    fm.addArc2(0.0, -r2, -90)
#    fm.addPoint(R, -C2+r2)
#    fm.addArc2(-r2, 0.0, -90)
#    fm.addPoint(rsC+r1, -C2)
#    fm.addArc2(0.0, r1, -90)
    fm.addPoint(rsC, C-r1)
    fm.addArc2(r1, 0.0, -90)
    fm.addPoint(R, C)
    fm.addPoint(R, 0.0)
    fm.addPoint(rsC+r1, 0.0)
    fm.addArc2(0.0, r1, -90)

#    shape2 = fm.getFace().revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)
    shape2 = fm.revolveZ(fm.getFace())

    shape = shape1.fuse(shape2)
#    shape0 = shape1.fuse(shape2)
#    shape = shape0.removeSplitter()

    return shape