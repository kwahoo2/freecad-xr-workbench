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
cube_cnt = 0
end_pnt = App.Vector(0, 0, 0)
# distance in mm where a point will be snapped to the last point
eps = 30.0


def add_line_start(cpnt):
    doc = App.ActiveDocument
    global line_cnt
    line_name = 'Line' + str(line_cnt)
    line_cnt = line_cnt + 1
    doc.addObject("Part::Line", line_name)
    line = doc.getObject(line_name)
    pnt = coint_to_doc_pnt(cpnt)
    # if a new point is close to old one, use the old location
    # useful for further conversion in polyline
    if (pnt.distanceToPoint(end_pnt) < eps):
        pnt = end_pnt
    line.X1 = pnt.x
    line.Y1 = pnt.y
    line.Z1 = pnt.z
    line.Placement = App.Placement(App.Vector(0, 0, 0),
                                   App.Rotation(App.Vector(0, 0, 1), 0))
    line.Label = line_name
    doc.recompute()


def move_line_end(cpnt):
    doc = App.ActiveDocument
    global line_cnt
    global end_pnt
    line_name = 'Line' + str(line_cnt - 1)
    line = doc.getObject(line_name)
    pnt = coint_to_doc_pnt(cpnt)
    end_pnt = pnt
    line.X2 = pnt.x
    line.Y2 = pnt.y
    line.Z2 = pnt.z


def add_cube(transf):
    doc = App.ActiveDocument
    global cube_cnt
    cube_name = 'Cube' + str(cube_cnt)
    cube_cnt = cube_cnt + 1
    doc.addObject("Part::Box", cube_name)
    doc.getObject(cube_name).Placement = coin_to_doc_placement(transf)
    doc.recompute()


def resize_cube(transf):
    doc = App.ActiveDocument
    cube_name = 'Cube' + str(cube_cnt - 1)
    cube = doc.getObject(cube_name)
    if cube:
        plac = cube.Placement
        p0 = plac.Base  # cube origin 0XYZ
        # vertex opposite to origin (diagonal) vertex of the cube
        pnt = coin_to_doc_placement(transf).Base
        vec = pnt - p0
        loc_x = (plac.Rotation * App.Vector(1, 0, 0))
        loc_y = (plac.Rotation * App.Vector(0, 1, 0))
        loc_z = (plac.Rotation * App.Vector(0, 0, 1))
        lx = loc_x * vec
        ly = loc_y * vec
        lz = loc_z * vec
        # if dragger in opposite dir, set dimension to 1mm, since negative is
        # not allowed
        cube.Length = lx if lx > 0 else 1
        cube.Width = ly if ly > 0 else 1
        cube.Height = lz if lz > 0 else 1


def coin_to_doc_placement(transf):
    coin_pos = transf.translation.getValue()
    pos = App.Vector(
        coin_pos.getValue()[0],
        coin_pos.getValue()[1],
        coin_pos.getValue()[2])
    coin_rot = transf.rotation.getValue()
    rot = App.Rotation(
        coin_rot.getValue()[0],
        coin_rot.getValue()[1],
        coin_rot.getValue()[2],
        coin_rot.getValue()[3])
    return App.Placement(pos, rot)


def coint_to_doc_pnt(cpnt):
    pnt = App.Vector(
        cpnt.getValue()[0],
        cpnt.getValue()[1],
        cpnt.getValue()[2])
    return pnt


def recompute():
    App.ActiveDocument.recompute()
