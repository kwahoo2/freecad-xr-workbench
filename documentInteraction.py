# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2024 Adrian Przekwas adrian.v.przekwas@gmail.com        *
# *                                                                         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 3 of     *
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

import FreeCAD as App
import Part

ppair = [App.Vector(), App.Vector()]

line_cnt = 0
pnt_cnt = 0
# distance in mm where a point will be snapped to the last point
eps = 30.0


def add_line():
    doc = App.ActiveDocument
    global line_cnt
    line_name = 'Line' + str(line_cnt)
    line_cnt = line_cnt + 1
    doc.addObject("Part::Line", line_name)
    line = doc.getObject(line_name)
    line.X1 = ppair[0].x
    line.Y1 = ppair[0].y
    line.Z1 = ppair[0].z
    line.X2 = ppair[1].x
    line.Y2 = ppair[1].y
    line.Z2 = ppair[1].z
    line.Placement = App.Placement(App.Vector(0, 0, 0),
                                   App.Rotation(App.Vector(0, 0, 1), 0))
    line.Label = line_name


def add_point(cpnt):
    global pnt_cnt
    global ppair
    # conversion from SbVec3f
    pnt = App.Vector(
        cpnt.getValue()[0],
        cpnt.getValue()[1],
        cpnt.getValue()[2])
    old_cnt = abs(pnt_cnt - 1)
    # if a new point is close to old one, use the old location
    # useful for further conversion in polyline
    if (pnt.distanceToPoint(ppair[old_cnt]) < eps):
        ppair[pnt_cnt] = ppair[old_cnt]
    else:
        ppair[pnt_cnt] = pnt
    pnt_cnt = pnt_cnt + 1
    if pnt_cnt > 1:
        pnt_cnt = 0
        add_line()
