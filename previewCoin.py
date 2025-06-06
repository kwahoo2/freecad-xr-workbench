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

from pivy.coin import SoSeparator
from pivy.coin import SoVertexProperty, SoLineSet, SoPointSet
from pivy.coin import SoSwitch, SoPickStyle, SO_SWITCH_NONE, SO_SWITCH_ALL
from pivy.coin import SoMaterial, SoCoordinate3, SoIndexedFaceSet
from pivy.coin import SoTransform
from pivy.coin import SO_END_FACE_INDEX

class coinPreview:
    def __init__(self):
        self.prev_sep = SoSeparator()

        self.draw_prev_sep = SoSwitch()
        self.draw_prev_sep.whichChild = SO_SWITCH_NONE

        self.working_plane_sep = SoSwitch()
        self.working_plane_sep.whichChild = SO_SWITCH_NONE

        self.prev_sep.addChild(self.draw_prev_sep)
        self.prev_sep.addChild(self.working_plane_sep)

        # one separator containts objects that can be picked (for snap)
        # other one unpickable objects, only for visualisation
        # we decide here to not snap to line we are drawing, just to
        # points at the ends of the finished lines
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
        self.plane_transform =  SoTransform()
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

    def get_scenegraph(self):
        return self.prev_sep

    def clean_preview(self):
        self.draw_prev_sep.whichChild = SO_SWITCH_NONE
        self.pline_vtxs.vertex.deleteValues(
            2)  # do not delete 2 first vertices
        self.pnt_vtxs.vertex.deleteValues(1)
        self.point_counter = 0

    def add_polyline(self, vec):
        self.pline_vtxs.vertex.set1Value(0, vec)
        self.pline_vtxs.vertex.set1Value(1, vec)
        self.pnt_vtxs.vertex.set1Value(0, vec)
        self.point_counter = 2
        self.draw_prev_sep.whichChild = SO_SWITCH_ALL

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

    def show_working_plane(self):
        self.working_plane_sep.whichChild = SO_SWITCH_ALL

    def hide_working_plane(self):
        self.working_plane_sep.whichChild = SO_SWITCH_NONE

    def toggle_working_plane(self):
        if self.working_plane_sep.whichChild.getValue() == SO_SWITCH_NONE:
            self.working_plane_sep.whichChild = SO_SWITCH_ALL
        else:
            self.working_plane_sep.whichChild = SO_SWITCH_NONE

    def update_working_plane(self, pos, rot):
        self.plane_transform.translation.setValue(pos)
        self.plane_transform.rotation.setValue(rot)

    def make_plane_pickable(self, pickable):
        if pickable:
            self.plane_pickable.style = SoPickStyle.SHAPE
        else:
            self.plane_pickable.style = SoPickStyle.UNPICKABLE
