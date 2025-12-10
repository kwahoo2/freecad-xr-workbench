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
import Draft

try:
    import UtilsAssembly
    has_utils_assembly = True
except ImportError:
    print ("UtilsAssembly not found, functionality will be limited")
    has_utils_assembly = False

from enum import Enum
import math
from pivy.coin import SbVec3f, SbRotation


class BuilderMode(Enum):
    NONE = 0
    LINE_BUILDER = 1
    CUBE_BUILDER = 2


builder_mode = BuilderMode.NONE

polyline_points = []

# last picked object dict
curr_sel = None
# last selected object
curr_obj = None
curr_draggable_obj = None
sel_pnt = App.Vector() # selection point
obj_plac_at_sel = App.Placement()
draggable_obj_plac_at_sel = App.Placement()
con_plac_at_sel = App.Placement()

polyline_cnt = 0
cube_cnt = 0
# distance in mm where a point will be snapped to the first point of the
# polyline
eps = 1.0


def set_mode(mode):
    global builder_mode
    builder_mode = mode
    print("Builder mode:", builder_mode)


def finish_building():
    if (builder_mode == BuilderMode.LINE_BUILDER):
        add_polyline()
        global polyline_points
        polyline_points = []


def add_polyline():
    global polyline_cnt
    global polyline_points
    if (len(polyline_points) < 2):
        return
    doc = App.ActiveDocument
    if (len(polyline_points) == 2):
        polyline_name = 'Line' + str(polyline_cnt)
    else:
        polyline_name = 'Polyline' + str(polyline_cnt)
    polyline_cnt = polyline_cnt + 1
    start_point = polyline_points[0]
    end_point = polyline_points[-1]
    # if a new point is close to starting point of the polyline, use the staring point location
    # useful for closing the polyline
    is_closed = False
    if (end_point.distanceToPoint(start_point) < eps):
        polyline_points[-1] = start_point
        is_closed = True
    polyline_points = adjust_coplanarity(polyline_points)
    polyline = Draft.make_wire(
        polyline_points,
        closed=is_closed,
        face=is_closed)
    polyline.Label = polyline_name
    recompute()


def add_polyline_point(cpnt):
    # conversion to document coordinates
    pnt = coin_to_doc_pnt(cpnt)
    global polyline_points
    polyline_points.append(pnt)
    print("Polyline point added", pnt, len(polyline_points))


def add_cube(transf):
    doc = App.ActiveDocument
    global cube_cnt
    cube_name = 'Cube' + str(cube_cnt)
    cube_cnt = cube_cnt + 1
    doc.addObject("Part::Box", cube_name)
    doc.getObject(cube_name).Placement = coin_to_doc_placement(transf)
    recompute()


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


def select_object(transform, view, point_coords = None):
    doc = App.ActiveDocument
    rot = transform.rotation.getValue()
    ray_axis = rot.multVec(SbVec3f(0, 0, 1))
    vec_start = coin_to_doc_pnt(transform.translation.getValue())
    if point_coords:
        # overwrite direction, for picking lines and points
        # selecting them with a controller ray is almost impossible
        vec_dir = coin_to_doc_pnt(point_coords) - vec_start
    else:
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
                if hasattr(p_obj, 'Placement'):
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

def get_selection_label():
    s = ""
    sub = ""
    selection = Gui.Selection.getSelectionEx()
    if len(selection):
        obj = selection[0].Object
        if obj:
            subs = selection[0].SubElementNames
            if len(subs):
                sub = subs[0]
            s = "Sel: "+ obj.Name + ", " + sub + " [Body: " + last_body_used +"]"
    return s

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
        if has_utils_assembly:
            if UtilsAssembly.activeAssembly():
                UtilsAssembly.activeAssembly().solve()
    # calculate the selection point new location
    s_pnt = plt_con * sel_pnt
    return s_pnt

# finds normal of the face in the selection point
def find_normal_sel():
    selection = Gui.Selection.getSelectionEx()
    obj = selection[0].Object
    subs = selection[0].SubElementNames
    if not len(subs):
        return None
    sub = subs[0]
    if sub.startswith('Face'):
        face_index = int(sub.split('Face')[1])
        # FreeCAD face index starts at 1
        face = obj.Shape.Faces[face_index - 1]
        u, v = face.Surface.parameter(sel_pnt)
        normal = face.normalAt(u, v)
        return normal
    else:
        return None

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
    if not dpnt:
        return None
    return SbVec3f(dpnt.x, dpnt.y, dpnt.z)


def doc_to_coin_rot(drot):
    if not drot:
        return None
    q = drot.Q
    rot = SbRotation(q[0], q[1], q[2], q[3])
    return rot

def recompute():
    App.ActiveDocument.recompute()


# this method adjusts points that are very close to be coplanar to be coplanar
# useful for making faces from more than 3 points
def adjust_coplanarity(points, eps_dist=0.5):
    if len(points) < 4:
        return points

    adjusted_points = points[:3]  # first 3 points define the plane
    v1 = points[1] - points[0]
    v2 = points[2] - points[0]
    normal = v1.cross(v2)
    normal.normalize()

    for point in points[3:]:
        vector = point - points[0]
        distance = vector.dot(normal)
        if abs(distance) < eps_dist:
            adjusted_point = point - normal * distance
            adjusted_points.append(adjusted_point)
            print("Point:", point, "adjusted to:", adjusted_point)
        else:
            adjusted_points.append(point)

    return adjusted_points


# Tools available in the edit menu below

class EditMode(Enum):
    NONE = 0
    PAD = 1
    POCKET = 2


edit_mode = EditMode.NONE

initial_edit_plac = App.Placement()

last_body_used = ""
curr_feature_obj = None
edit_sel_pnt = None
edit_started = False
length = 0


def update_edit_transf(transform):
    if not edit_sel_pnt:
        return
    con_plac = coin_to_doc_placement(transform)
    old_con_plac = initial_edit_plac
    # calculating transformation between two controller poses
    plt_con = con_plac * old_con_plac.inverse()
    # update original selection point location with controller transformation
    s_pnt = plt_con * edit_sel_pnt

    global length
    normal = find_normal_sel()
    if normal:
        # we assume the feature is extended in normal direction to selection
        length = s_pnt.distanceToPlane(edit_sel_pnt, normal)
    else:
        return
    if edit_mode == EditMode.PAD:
        if not curr_feature_obj:
            return
        if not curr_feature_obj.TypeId == 'PartDesign::Pad':
            return
    elif edit_mode == EditMode.POCKET:
        if not curr_feature_obj:
            return
        if not curr_feature_obj.TypeId == 'PartDesign::Pocket':
            return
    if (edit_mode == EditMode.PAD
            or edit_mode == EditMode.POCKET):
        curr_feature_obj.UseCustomVector = True
        # otherwise custom vector would produce wrong length in reality
        # this will not be necessary if the placement of the face is aligned with its vertices
        curr_feature_obj.AlongSketchNormal = True
        abs_length = abs(length)
        if abs_length < 0.1: # avoid 0 length feature at the start of dragging
            abs_length = 0.1
        curr_feature_obj.Length = abs_length
        curr_feature_obj.Direction = normal
        if length > 0:
            curr_feature_obj.Reversed = False
        else:
            curr_feature_obj.Reversed = True
        recompute()

    return s_pnt


def set_start_edit(transform, view):
    doc = App.ActiveDocument
    rot = transform.rotation.getValue()
    ray_axis = rot.multVec(SbVec3f(0, 0, 1))
    vec_start = coin_to_doc_pnt(transform.translation.getValue())
    vec_dir = coin_to_doc_pnt(-ray_axis)
    # Document objects picking, Base::Vector is needed, not SbVec3f
    info = view.getObjectInfoRay(vec_start, vec_dir)
    global edit_sel_pnt
    edit_sel_pnt = None
    if (info):
        edit_sel_pnt = info['PickedPoint']
    else:
        return
    global initial_edit_plac
    initial_edit_plac = coin_to_doc_placement(transform)
    global curr_feature_obj, curr_obj
    selection = Gui.Selection.getSelectionEx()
    curr_obj = selection[0].Object
    if not curr_obj:
        return
    curr_feature_obj = None
    sub_objs =  ['',]
    if (curr_obj.TypeId == 'PartDesign::Pad'
        or curr_obj.TypeId == 'PartDesign::Pocket'):
        subs = selection[0].SubElementNames
        if len(subs):
            sub_objs = [subs[0],]
    if edit_mode == EditMode.PAD:
        body = find_add_body()
        if not curr_obj: # asking again, since adding obj to the Body might fail
            return
        curr_feature_obj = body.newObject('PartDesign::Pad', 'Pad')
        curr_feature_obj.Profile = (curr_obj, sub_objs)
        curr_obj.ViewObject.Visibility = False
        curr_feature_obj.ViewObject.Visibility = True
    elif edit_mode == EditMode.POCKET:
        # subtractive feature cannot be first, so don't allow Body creation
        body = find_body()
        if not curr_obj:
            return
        curr_feature_obj = body.newObject('PartDesign::Pocket', 'Pocket')
        curr_feature_obj.Profile = (curr_obj, sub_objs)
        curr_obj.ViewObject.Visibility = False
        curr_feature_obj.ViewObject.Visibility = True
    global edit_started
    edit_started = True


def set_finish_edit():
    global edit_started
    global edit_mode
    if edit_started:
        if (edit_mode == EditMode.PAD
                or edit_mode == EditMode.POCKET):
            edit_sel_pnt = None
            recompute()
        edit_started = False
        edit_mode = EditMode.NONE
        global curr_feature_obj, curr_obj
        curr_obj = None
        curr_feature_obj = None


def create_pad():
    global edit_mode
    edit_mode = EditMode.PAD


def create_pocket():
    global edit_mode
    edit_mode = EditMode.POCKET


def get_edit_info():
    return edit_mode, length


def create_body():
    doc = App.ActiveDocument
    body = doc.addObject("PartDesign::Body", "Body")
    Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", body)
    global last_body_used
    last_body_used = body.Name


def activate_last_body():
    doc = App.ActiveDocument
    body = doc.getObject(last_body_used)
    if body:
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", body)
    return body


def delete_sel_obj():
    selection = Gui.Selection.getSelectionEx()
    if len(selection):
        obj = selection[0].Object
        doc = App.ActiveDocument
        print("Deleting object:", obj.Name)
        doc.removeObject(obj.Name)

# This checks if an object belongs to a body.
# If not, it add the object to the last selected body.
# If no body exists it created one (note this does not search for all
# bodies, just uses last one created in session).


def find_add_body():
    global last_body_used
    global curr_obj
    if curr_obj:
        obj = curr_obj
        doc = App.ActiveDocument
    else:
        return None
    body = find_body()
    if not body:
        body = doc.addObject('PartDesign::Body', 'Body')
        Gui.ActiveDocument.ActiveView.setActiveObject("pdbody", body)
        # special case for Draft Wires, since they are not treated as 2D objects anymore
        if obj.TypeId == 'Part::FeaturePython' and obj.Shape.ShapeType == 'Face':
            obj.Visibility = False
            obj = Draft.make_sketch(obj, autoconstraints=True)
            curr_obj = obj
        try:
            body.addObject(obj)
        except Exception as e: # some objects, like Part objs cannot be added directly
            obj.adjustRelativeLinks(body)
            body.ViewObject.dropObject(obj,None,'',[])
            clear_selection()
        last_body_used = body.Name
    return body


def find_body():
    global curr_obj
    if curr_obj:
        obj = curr_obj
        doc = App.ActiveDocument
    else:
        return None
    parent = obj.getParentGeoFeatureGroup()
    if parent and parent.TypeId == 'PartDesign::Body':
        return parent
    else:
        body = activate_last_body()
        if body:
            try:
                body.addObject(obj)
            except Exception as e:
                obj.adjustRelativeLinks(body)
                body.ViewObject.dropObject(obj,None,'',[])
                clear_selection()
            return body
        else:
            return None


# subtractive features require some solid to sutract from


def is_body_solid(body):
    if not body:
        return False
    try:
        if body.Shape.isValid() and body.Shape.Solids:
            return True
        else:
            return False
    except Part.OCCError:
        return False


def has_obj():
    return curr_obj
