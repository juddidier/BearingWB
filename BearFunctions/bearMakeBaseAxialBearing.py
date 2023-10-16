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
import Draft
import math
from BearMaker import *
import BearUtils

T_CAGE = 0.2
DEPTH_SHIELD = 0.2
TOT_DEPTH = 0.5

def MakeBaseAxialBearing(self, fp):
#    FreeCAD.Console.PrintMessage("makeBaseAxialBearing()\n")

#    FreeCAD.Console.PrintMessage(fp.type)
#    FreeCAD.Console.PrintMessage(" - ")
#    FreeCAD.Console.PrintMessage(fp.sizeCode)
#    FreeCAD.Console.PrintMessage("\n")

    d1, D2, B, B1, d1inside, D2inside, Ds, dBall, nB, rClip, gap = bearMaker.bearData[fp.type+"_def"][fp.sizeCode]
    if hasattr(fp, 'shield') and fp.shield != '-':
        b = B1
    else:
        b = B
    nBall = int(nB)
    r1 = d1 / 2
    R2 = D2 / 2
    r1ins = d1inside / 2
    R2ins = D2inside / 2
    Rs = Ds / 2

    dRr = (R2ins - r1ins)/2
    rBall = dBall / 2
    hBall = math.sqrt(rBall*rBall - dRr*dRr)

    fm = BearUtils.bearFaceMaker()
    fm.addPoint(r1, b-Rs)
    fm.addArc2(Rs, 0.0, -90)
    fm.addPoint(r1ins, b)

    if B1 > 0.0 and hasattr(fp, 'shield') and fp.shield != '-':      # draw shield on upper side
#        if B1 > 0.0:
            if gap > 0.0:
                fm.addPoints((r1ins, b-0.5),
                             (r1ins+gap, b-0.5))
            fm.addPoints((r1ins+gap, b-0.2),
                         (R2ins-2*rClip, b-0.2),
                         (R2ins-rClip, b-rClip-0.1))
            fm.addArc2(rClip, 0.0, -90)
#        else:
#            fm.addPoints((r1ins, b-0.2),(R2ins, b-0.2))
    else:                                                             # draw balls on upper side
        fm.addPoint(r1ins, b/2 + hBall + T_CAGE)
        fm.addPoint(R2ins, b/2 + hBall + T_CAGE)

    fm.addPoint(R2ins,b)
    fm.addPoint(R2-Rs, b)
    fm.addArc2(0.0, -Rs, -90)
    fm.addPoint(R2, Rs)
    fm.addArc2(-Rs, 0.0, -90)
    fm.addPoint(R2ins,0.0)

    if B1 > 0.0 and hasattr(fp, 'shield') and (fp.shield == '2Z' or fp.shield == '2RS'):      # draw shield on lower side
        fm.addPoint(R2ins, 0.1)
        fm.addArc2(0.0, rClip, -90)
        fm.addPoints((R2ins-2*rClip, 0.2), (r1ins+gap, 0.2))
        if gap > 0.0:
            fm.addPoints((r1ins+gap, 0.5),(r1ins, 0.5))
    else:                                                                                      # draw balls on lower side
        fm.addPoint(R2ins, b/2 - hBall - T_CAGE)
        fm.addPoint(r1ins, b/2 - hBall - T_CAGE)

    fm.addPoint(r1ins, 0.0)
    fm.addPoint(r1+Rs, 0.0)
    fm.addArc2(0.0, Rs, -90)
#    shape = fm.revolveZ(fm.getFace)
    face = fm.getFace()
#    FreeCAD.Console.PrintMessage(face.__dir__())
#    FreeCAD.Console.PrintMessage("\n")
    shape = face.revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)

    if B1 == 0.0 or not hasattr(fp, 'shield') or (hasattr(fp, 'shield') and (fp.shield != '2Z' or fp.shield != '2RS')):     # draw balls
        angle = 2 * math.pi / nBall
        radius = (R2ins + r1ins) / 2
        balls = []
        for n in range(nBall):
            xp = radius * math.cos(n * angle)
            yp = radius * math.sin(n * angle)
            ball = Part.makeSphere(rBall+T_CAGE)
            ball.Placement.Base.x = xp
            ball.Placement.Base.y = yp
            ball.Placement.Base.z = b / 2
            balls.append(ball)

        shape = shape.fuse(balls)

    return shape