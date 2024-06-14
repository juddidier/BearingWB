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
#import math
from BearMaker import *
import BearUtils


def MakeNeedleRollerThrustBearing(self, fp):

    d1, D2, Bw, Ea, Eb, dNeedle, nNeedleFloat = bearMaker.bearData[fp.type+"_def"][fp.sizeCode]
    w_d1, w_D, w_D1, w_B, w_r12 = bearMaker.bearData[fp.type+"_washerDef"][fp.sizeCode]
    nNeedle = int(nNeedleFloat)
    r1 = d1 / 2
    R2 = D2 / 2

    rNeedle = dNeedle / 2
    w_r = r1
    w_r1 = w_d1 / 2
    w_R = w_D / 2
    w_R1 = w_D1 / 2

    centerNeedle = rNeedle

    botWshape = None
    topWshape = None

    if hasattr(fp, 'bottomWasher'):
        botW = BearUtils.bearFaceMaker()

        attrib = str(getattr(fp, 'bottomWasher'))
        if attrib == 'LS':
            centerNeedle += w_B
            botW.addPoints((w_r, w_r12),(w_r, w_B),(w_R, w_B),(w_R, w_r12),(w_R - w_r12, 0.0),(w_r + w_r12, 0.0))
        elif attrib == 'AS':
            centerNeedle += 1.0
            botW.addPoints((w_r, 0.0),(w_r, 1.0),(w_R, 1.0), (w_R, 0.0))
        if botW.hasShape():
            botWshape = botW.getFace().revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)

    if hasattr(fp, 'topWasher'):
        topWbase = centerNeedle + rNeedle
        topW = BearUtils.bearFaceMaker()

        attrib = str(getattr(fp, 'topWasher'))
        if attrib == 'LS':
            topW.addPoints((w_r, topWbase), (w_r, topWbase + w_B - w_r12), (w_r + w_r12, topWbase + w_B),(w_R - w_r12, topWbase + w_B),(w_R, topWbase + w_B - w_r12),(w_R, topWbase))
        if attrib == 'AS':
            topW.addPoints((w_r, topWbase), (w_r, topWbase + 1.0),(w_R, topWbase + 1.0),(w_R, topWbase))
        if topW.hasShape():
            topWshape = topW.getFace().revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)

    needles = []
    lenNeedle = (Eb - Ea) / 2
    angle = 360 / nNeedleFloat

    needle = Part.makeCylinder(rNeedle, lenNeedle, FreeCAD.Base.Vector(Ea/2, 0.0, centerNeedle),FreeCAD.Base.Vector(1, 0, 0), 360)
    for n in range(nNeedle):
        needles.append(needle.rotated(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), n * angle))
    shape = Part.makeCylinder(R2, Bw, FreeCAD.Base.Vector(0.0, 0.0, centerNeedle - Bw/2))#, FreeCAD.Base.Vector(0, 0, 1), 360)
    shape = shape.cut(Part.makeCylinder(r1, Bw, FreeCAD.Base.Vector(0.0, 0.0, centerNeedle - Bw/2)))#, FreeCAD.Base.Vector(0, 0, 1), 360))
    shape = shape.fuse(needles)

    if botWshape != None:
        shape = shape.fuse(botWshape)
    if topWshape != None:
        shape = shape.fuse(topWshape)

    return shape
