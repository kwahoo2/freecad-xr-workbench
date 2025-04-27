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
from pivy.coin import SoVertexProperty, SoLineSet
from pivy.coin import SoSwitch, SoPickStyle, SO_SWITCH_NONE, SO_SWITCH_ALL


class coinPreview:
    def __init__(self):
        self.prev_sep = SoSwitch()
        self.prev_sep.whichChild = SO_SWITCH_NONE
        # one separator containts objects that can be picked (for snap)
        # other one unpickable objects, only for visualisation

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

        self.prev_sep.addChild(self.not_pick_sep)

        self.point_counter = 0

    def get_scenegraph(self):
        return self.prev_sep

    def clean_preview(self):
        self.prev_sep.whichChild = SO_SWITCH_NONE
        self.pline_vtxs.vertex.deleteValues(
            2)  # do not delete 2 first vertices
        self.point_counter = 0

    def add_polyline(self, vec):
        self.pline_vtxs.vertex.set1Value(0, vec)
        self.pline_vtxs.vertex.set1Value(1, vec)
        self.point_counter = 2
        self.prev_sep.whichChild = SO_SWITCH_ALL

    def add_polyline_node(self, vec):
        if self.point_counter:
            self.pline_vtxs.vertex.set1Value(self.point_counter, vec)
            self.point_counter += 1
        else:
            self.add_polyline(vec)

    def move_last_polyline_node(self, vec):
        if self.pline_vtxs:
            count = self.pline_vtxs.vertex.getNum()
            self.pline_vtxs.vertex.set1Value(count - 1, vec)
