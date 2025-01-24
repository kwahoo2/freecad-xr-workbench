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
import FreeCADGui as Gui
import Part
import UtilsAssembly

from pivy.coin import SbVec3f

ppair = [App.Vector(), App.Vector()]

# last picked object dict
curr_sel = None
# last selected object
curr_obj = None
curr_draggable_obj = None
sel_pnt = App.Vector()
obj_plac_at_sel = App.Placement()
draggable_obj_plac_at_sel = App.Placement()
con_plac_at_sel = App.Placement()

line_cnt = 0
cube_cnt = 0
end_pnt = App.Vector()
# distance in mm where a point will be snapped to the last point
eps = 30.0


def add_line_start(cpnt):
    doc = App.ActiveDocument
    global line_cnt
    line_name = 'Line' + str(line_cnt)
    line_cnt = line_cnt + 1
    doc.addObject("Part::Line", line_name)
    line = doc.getObject(line_name)
    pnt = coin_to_doc_pnt(cpnt)
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
    pnt = coin_to_doc_pnt(cpnt)
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


def select_object(transform, view):
    doc = App.ActiveDocument
    rot = transform.rotation.getValue()
    ray_axis = rot.multVec(SbVec3f(0, 0, 1))
    vec_start = coin_to_doc_pnt(transform.translation.getValue())
    vec_dir = coin_to_doc_pnt(-ray_axis)
    # Document objects picking, Base::Vector is needed, not SbVec3f
    info = view.getObjectInfoRay(vec_start, vec_dir)
    if (info):
        sect_pt = info['PickedPoint']
        Gui.Selection.addSelection(
            info['Document'],
            info['Object'],
            info['Component'],
            sect_pt.x,
            sect_pt.y,
            sect_pt.z)
        global curr_sel, curr_obj, sel_pnt, curr_draggable_obj
        global con_plac_at_sel, obj_plac_at_sel, draggable_obj_plac_at_sel
        curr_sel = info
        curr_obj = doc.getObject(info['Object'])
        sel_pnt = sect_pt
        con_plac_at_sel = coin_to_doc_placement(transform)
        if hasattr(curr_obj, 'Placement'):
            obj_plac_at_sel = curr_obj.Placement
        print("XR selection: ", info)
        # find object that can be used for dragging (the highest level object
        # (could be Part, Body...), except AssemblyObject)
        parent = ''
        if 'ParentObject' in info:
            parent = info['ParentObject']
        p_obj = doc.getObject(parent)
        sub_n = ''
        if 'SubName' in info:
            sub_n = info['SubName']
        sub_obj = sub_n.split(".")
        if p_obj:
            if p_obj.TypeId == 'Assembly::AssemblyObject':
                # find the first non-assembly object
                for s in sub_obj:
                    o = doc.getObject(s)
                    if o:
                        if o.TypeId != 'Assembly::AssemblyObject' and hasattr(
                                o, 'Placement'):
                            curr_draggable_obj = o
                            draggable_obj_plac_at_sel = o.Placement
                            return
            else:
                if hasattr(o, 'Placement'):
                    curr_draggable_obj = p_obj
                    draggable_obj_plac_at_sel = p_obj.Placement
                else:
                    for s in sub_obj:
                        o = doc.getObject(s)
                        if o:
                            if hasattr(o, 'Placement'):
                                curr_draggable_obj = o
                                draggable_obj_plac_at_sel = o.Placement
                                return
        elif hasattr(curr_obj, 'Placement'):
            curr_draggable_obj = curr_obj
            draggable_obj_plac_at_sel = curr_obj.Placement


def clear_selection():
    Gui.Selection.clearSelection()
    global curr_sel, curr_obj, curr_draggable_obj
    curr_obj = None
    curr_sel = None
    curr_draggable_obj = None


def drag_object(transform):
    con_plac = coin_to_doc_placement(transform)
    old_obj_plac = draggable_obj_plac_at_sel
    old_con_plac = con_plac_at_sel
    # calculating transformation between two controller poses
    plt_con = con_plac * old_con_plac.inverse()
    # calculate the selected obj new placement
    draggable_obj_plac = plt_con * old_obj_plac
    if (curr_draggable_obj):
        curr_draggable_obj.Placement = draggable_obj_plac
        if UtilsAssembly.activeAssembly():
            UtilsAssembly.activeAssembly().solve()
    # calculate the selection point new location
    s_pnt = plt_con * sel_pnt
    return s_pnt


def get_sel_sbvec():
    sb_vec = None
    if (curr_sel):
        if (curr_sel['PickedPoint']):
            vec = curr_sel['PickedPoint']
            sb_vec = doc_to_coin_pnt(vec)
    return sb_vec


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


def coin_to_doc_pnt(cpnt):
    pnt = App.Vector(
        cpnt.getValue()[0],
        cpnt.getValue()[1],
        cpnt.getValue()[2])
    return pnt


def doc_to_coin_pnt(dpnt):
    return SbVec3f(dpnt.x, dpnt.y, dpnt.z)


def recompute():
    App.ActiveDocument.recompute()
