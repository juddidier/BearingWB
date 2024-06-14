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
from BearMaker import *
import BearUtils

def MakeRoundLinearBearing(self, fp):
    dr, D, L, B, D1, W, a, b = bearMaker.bearData[fp.type+"_def"][fp.sizeCode]
    ri = dr / 2
    ro = D / 2
    r1o = D1 / 2
    LB2 = (L - B) / 2

    fm = BearUtils.bearFaceMaker()
    fm.addPoints((ro-a, 0.0),
                 (ro, b))
    if B > 0.0:
        fm.addPoints((ro, LB2),
                     (r1o, LB2),
                     (r1o, LB2+W),
                     (ro, LB2+W),
                     (ro, L-LB2-W),
                     (r1o, L-LB2-W),
                     (r1o, L-LB2),
                     (ro, L-LB2))
    fm.addPoints((ro, L-a),
                 (ro-a, L),
                 (ro-2*a, L),
                 (ro-2*a, L-b),
                 (ri+a, L-b),
                 (ri+a, L),
                 (ri, L),
                 (ri, L-2*b))
    fm.addPoints((ri, 2*b),
                 (ri, 0.0),
                 (ri+a, 0.0),
                 (ri+a, b),
                 (ro-2*a, b),
                 (ro-2*a, 0.0))
    face = fm.getFace()
    shape = face.revolve(FreeCAD.Base.Vector(0, 0, 0), FreeCAD.Base.Vector(0, 0, 1), 360)
    return shape