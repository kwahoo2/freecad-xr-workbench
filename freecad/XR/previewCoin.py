# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2025 Adrian Przekwas adrian.v.przekwas@gmail.com        *
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

from freecad.XR.menuCoin import labelWidget
from freecad.XR.documentInteraction import EditMode

from pivy.coin import SoSeparator
from pivy.coin import SoVertexProperty, SoLineSet, SoPointSet
from pivy.coin import SoSwitch, SoPickStyle, SO_SWITCH_NONE, SO_SWITCH_ALL
from pivy.coin import SoMaterial, SoCoordinate3, SoIndexedFaceSet
from pivy.coin import SoTransform, SbRotation, SbVec3f
from pivy.coin import SO_END_FACE_INDEX


class coinPreview:
    def __init__(self):
        self.prev_sep = SoSeparator()

        self.draw_prev_sep = SoSwitch()
        self.draw_prev_sep.whichChild = SO_SWITCH_NONE

        self.working_plane_switch = SoSwitch()
        self.working_plane_switch.whichChild = SO_SWITCH_NONE
        # separate working plane to not pollute other nodes with its material
        self.working_plane_sep = SoSeparator()
        self.working_plane_switch.addChild(self.working_plane_sep)

        self.line_labels_switch = SoSwitch()
        self.line_labels_switch.whichChild = SO_SWITCH_NONE

        self.feature_labels_switch = SoSwitch()
        self.feature_labels_switch.whichChild = SO_SWITCH_NONE

        self.prev_sep.addChild(self.draw_prev_sep)
        self.prev_sep.addChild(self.working_plane_switch)
        self.prev_sep.addChild(self.line_labels_switch)
        self.prev_sep.addChild(self.feature_labels_switch)

        # one separator contains objects that can be picked (for snap)
        # other one unpickable objects, only for visualisation
        # we decide here to not snap to line we are drawing, instead
        # to points at the ends of the finished lines
        self.not_pick_sep = SoSeparator()
        unpickable = SoPickStyle()
        unpickable.style = SoPickStyle.UNPICKABLE
        self.not_pick_sep.addChild(unpickable)
        self.pline_vtxs = SoVertexProperty()
        self.polyline = SoLineSet()
        self.pline_vtxs.vertex.set1Value(0, 0, 0, 0)
        self.pline_vtxs.vertex.set1Value(1, 0, 0, 0)
        self.polyline.vertexProperty = self.pline_vtxs
        self.not_pick_sep.addChild(self.polyline)

        self.pick_sep = SoSeparator()
        pickable = SoPickStyle()
        pickable.style = SoPickStyle.SHAPE
        self.pick_sep.addChild(pickable)
        self.pnt_vtxs = SoVertexProperty()
        self.pnts = SoPointSet()
        self.pnt_vtxs.vertex.set1Value(0, 0, 0, 0)
        self.pnts.vertexProperty = self.pnt_vtxs
        self.pick_sep.addChild(self.pnts)

        self.draw_prev_sep.addChild(self.not_pick_sep)
        self.draw_prev_sep.addChild(self.pick_sep)

        self.point_counter = 0

        # half-transparent working plane implemenentation
        self.plane_transform = SoTransform()
        self.working_plane_sep.addChild(self.plane_transform)
        self.plane_pickable = SoPickStyle()
        self.plane_pickable.style = SoPickStyle.SHAPE
        self.working_plane_sep.addChild(self.plane_pickable)
        material = SoMaterial()
        material.diffuseColor.setValue(0.0, 0.0, 1.0)
        material.transparency.setValue(0.5)
        self.working_plane_sep.addChild(material)

        coords = SoCoordinate3()
        coords.point.set1Value(0, -10.0, -10.0, 0.0)
        coords.point.set1Value(1, 10.0, -10.0, 0.0)
        coords.point.set1Value(2, 10.0, 10.0, 0.0)
        coords.point.set1Value(3, -10.0, 10.0, 0.0)
        self.working_plane_sep.addChild(coords)

        faceSet = SoIndexedFaceSet()
        faceSet.coordIndex.setValues(0, 5, [0, 1, 2, 3, SO_END_FACE_INDEX])
        self.working_plane_sep.addChild(faceSet)

        # accounting worldtransformation (artificial movement)
        self.hmdrot_glob = SbRotation()
        self.hmdpos_glob = SbVec3f()

        # show line verices coordinates and line length
        self.coord_label = labelWidget(text="(0.00, 0.00, 0.00)", scale=0.005)
        self.line_labels_switch.addChild(self.coord_label.get_scenegraph())

        self.length_label = labelWidget(text="L=0.00", scale=0.005)
        self.line_labels_switch.addChild(self.length_label.get_scenegraph())

        # reuse already created label as a feature label
        self.feature_labels_switch.addChild(self.length_label.get_scenegraph())

    def get_scenegraph(self):
        return self.prev_sep

    def update_hmd(self, hmd_transform, world_transform):
        self.hmdrot_glob = hmd_transform.rotation.getValue() * \
            world_transform.rotation.getValue()
        self.hmdpos_glob = hmd_transform.translation.getValue(
        ) + world_transform.translation.getValue()

    def update_coord_label(self, vec):
        self.coord_label.set_text(
            f'({vec.getValue()[0]:.2f}' + ', ' + f'{vec.getValue()[1]:.2f}' + ', ' + f'{vec.getValue()[2]:.2f})')

    def update_length_label(self, vec_len, prefix="L="):
        self.length_label.set_text(f'{prefix}{vec_len:.2f}')

    def get_vertex_pair_pos(self):
        # returns location of last two vertices, start and end of current edge
        if self.pline_vtxs:
            count = self.pline_vtxs.vertex.getNum()
            return self.pline_vtxs.vertex[count - 2], self.pline_vtxs.vertex[count - 1]
        return None

    def clean_polyline_preview(self):
        self.draw_prev_sep.whichChild = SO_SWITCH_NONE
        self.line_labels_switch.whichChild = SO_SWITCH_NONE
        self.feature_labels_switch.whichChild = SO_SWITCH_NONE
        self.pline_vtxs.vertex.deleteValues(
            2)  # do not delete first 2 vertices
        self.pnt_vtxs.vertex.deleteValues(1)
        self.point_counter = 0

    def clean_feature_preview(self):
        self.feature_labels_switch.whichChild = SO_SWITCH_NONE

    def add_polyline(self, vec):
        self.pline_vtxs.vertex.set1Value(0, vec)
        self.pline_vtxs.vertex.set1Value(1, vec)
        self.pnt_vtxs.vertex.set1Value(0, vec)
        self.point_counter = 2
        self.draw_prev_sep.whichChild = SO_SWITCH_ALL
        self.line_labels_switch.whichChild = SO_SWITCH_ALL

    def add_polyline_node(self, vec):
        if self.point_counter:
            self.pline_vtxs.vertex.set1Value(self.point_counter, vec)
            self.pnt_vtxs.vertex.set1Value(self.point_counter - 1, vec)
            self.point_counter += 1
        else:
            self.add_polyline(vec)

    def move_last_polyline_node(self, vec):
        if self.pline_vtxs:
            count = self.pline_vtxs.vertex.getNum()
            self.pline_vtxs.vertex.set1Value(count - 1, vec)
            # label near to the vertex
            self.coord_label.set_location(vec, self.hmdrot_glob)
            old_vec = self.pline_vtxs.vertex[count - 2]
            self.length_label.set_location(
                ((vec + old_vec) / 2), self.hmdrot_glob)

    def show_working_plane(self):
        self.working_plane_switch.whichChild = SO_SWITCH_ALL

    def hide_working_plane(self):
        self.working_plane_switch.whichChild = SO_SWITCH_NONE

    def toggle_working_plane(self):
        if self.working_plane_switch.whichChild.getValue() == SO_SWITCH_NONE:
            self.working_plane_switch.whichChild = SO_SWITCH_ALL
        else:
            self.working_plane_switch.whichChild = SO_SWITCH_NONE

    def update_working_plane(self, pos, rot):
        self.plane_transform.translation.setValue(pos)
        self.plane_transform.rotation.setValue(rot)

    def make_plane_pickable(self, pickable):
        if pickable:
            self.plane_pickable.style = SoPickStyle.SHAPE
        else:
            self.plane_pickable.style = SoPickStyle.UNPICKABLE

    def set_feature_label(self, edit_mode, length, i_sec_xr):
        # label for pads/pockets
        self.feature_labels_switch.whichChild = SO_SWITCH_ALL
        if edit_mode == EditMode.PAD:
            self.update_length_label(length, "Pad L=")
        if edit_mode == EditMode.POCKET:
            self.update_length_label(length, "Pocket L=")
        # place label in the 3/4 between user head and feature
        self.length_label.set_location(
            ((3 * i_sec_xr + self.hmdpos_glob) / 4), self.hmdrot_glob)
