# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Adrian Przekwas adrian.v.przekwas@gmail.com        *
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

import logging

import os

from dataclasses import dataclass

from pivy.coin import SoSeparator
from pivy.coin import SbVec3f, SbRotation
from pivy.coin import SoTransform, SoTranslation
from pivy.coin import SoCube, SoSphere
from pivy.coin import SoInput, SoDB
from pivy.coin import SoVertexProperty, SoLineSet
from pivy.coin import SoBaseColor, SbColor
from pivy.coin import SoRayPickAction
from pivy.coin import SoSwitch, SO_SWITCH_NONE, SO_SWITCH_ALL


@dataclass
class ButtonsState:
    grab: float = 0.0
    lever_x: float = 0.0
    lever_y: float = 0.0


class xrController:
    def __init__(self, iden=0, ray=False, log_level=logging.WARNING):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        # this node contains everything that moves with controller, SoSwitch
        # can behave like a standard node
        self.controller_node = SoSwitch()
        self.controller_node.whichChild = SO_SWITCH_ALL
        self.iden = iden
        self.buttons_state = ButtonsState()
        self.con_localtransform = SoTransform()
        self.con_transform = SoTransform()
        if ray:
            self.ray_node = SoSwitch()
            self.add_picking_ray()
            self.update_ray_axis()
        else:
            self.ray_node = None
        self.add_controller_shape()

    def add_controller_shape(self):
        con_sep = SoSeparator()
        con_node = None
        # Read the file
        if self.iden == 0:
            con_node = self.read_file(os.path.join(
                os.path.dirname(__file__), "controllers", "left_con.iv")
            )
        if self.iden == 1:
            con_node = self.read_file(os.path.join(
                os.path.dirname(__file__), "controllers", "right_con.iv")
            )
        if (con_node is None):
            con_node = SoSeparator()
            con_cube = SoCube()
            con_cube.width.setValue(0.05)
            con_cube.height.setValue(0.025)
            con_cube.depth.setValue(0.15)
            # replace controller with simple cube if the iv file not found
            con_node.addChild(con_cube)
        con_sep.addChild(self.con_transform)
        con_sep.addChild(con_node)
        self.controller_node.addChild(con_sep)

    def add_picking_ray(self):
        self.ray_vtxs = SoVertexProperty()
        # set first vertex, later update to center of the controller (global
        # location)
        self.ray_vtxs.vertex.set1Value(0, 0, 0, 0)
        # set second vertex, later update to point of intersection ray with hit
        # object (global location)
        self.ray_vtxs.vertex.set1Value(1, 0, 0, 1)
        ray_line = SoLineSet()
        ray_line.vertexProperty = self.ray_vtxs
        ray_color = SoBaseColor()
        ray_color.rgb = SbColor(1, 0, 0)
        # required since SoSwitch behaves like a node not like a separator
        ray_sep = SoSeparator()
        ray_sep.addChild(ray_color)
        ray_sep.addChild(ray_line)
        self.sph_trans = SoTranslation()
        self.sph_trans.translation.setValue(0, 0, 0)
        ray_sep.addChild(self.sph_trans)
        ray_sph = SoSphere()
        ray_sph.radius.setValue(0.02)
        ray_sep.addChild(ray_sph)
        self.ray_node.addChild(ray_sep)

    def get_controller_scenegraph(self):
        return self.controller_node

    def get_ray_scenegraph(self):
        return self.ray_node

    def update_pose(self, space_location, world_transform):
        con_rot = SbRotation(
            space_location.pose.orientation.x,
            space_location.pose.orientation.y,
            space_location.pose.orientation.z,
            space_location.pose.orientation.w)
        con_pos = SbVec3f(
            space_location.pose.position.x,
            space_location.pose.position.y,
            space_location.pose.position.z)
        con_worldtransform = SoTransform()
        con_worldtransform.translation.setValue(
            world_transform.translation.getValue())
        con_worldtransform.rotation.setValue(
            world_transform.rotation.getValue())
        con_worldtransform.center.setValue(world_transform.center.getValue())
        self.con_localtransform.translation.setValue(con_pos)
        self.con_localtransform.rotation.setValue(con_rot)
        # combine real hmd and artificial (stick-driven) movement
        con_worldtransform.combineLeft(self.con_localtransform)
        self.con_transform.rotation.setValue(
            con_worldtransform.rotation.getValue())
        self.con_transform.translation.setValue(
            con_worldtransform.translation.getValue())
        self.con_transform.center.setValue(SbVec3f(0, 0, 0))

    def update_ray_axis(self):
        gqx = self.con_transform.rotation.getValue().getValue()[0]
        gqy = self.con_transform.rotation.getValue().getValue()[1]
        gqz = self.con_transform.rotation.getValue().getValue()[2]
        gqw = self.con_transform.rotation.getValue().getValue()[3]

        gmat02 = 2 * gqx * gqz + 2 * gqy * gqw
        gmat12 = 2 * gqy * gqz - 2 * gqx * gqw
        gmat22 = 1 - 2 * gqx * gqx - 2 * gqy * gqy
        self.ray_axis = SbVec3f(gmat02, gmat12, gmat22)

    def show_ray(self):
        if (self.ray_node):
            self.ray_node.whichChild = SO_SWITCH_ALL

    def hide_ray(self):
        if (self.ray_node):
            self.ray_node.whichChild = SO_SWITCH_NONE

    def show_controller(self):
        self.controller_node.whichChild = SO_SWITCH_ALL

    def hide_controller(self):
        self.controller_node.whichChild = SO_SWITCH_NONE

    def find_picked_coin_object(
            self,
            separator,
            vp_reg,
            near_plane,
            far_plane):
        self.update_ray_axis()
        ray_start_vec = self.con_transform.translation.getValue()
        ray_end_vec = self.con_transform.translation.getValue() - self.ray_axis

        # picking ray
        con_pick_action = SoRayPickAction(vp_reg)
        # direction is reversed controller Z axis
        con_pick_action.setRay(
            ray_start_vec, -self.ray_axis, near_plane, far_plane)

        self.ray_vtxs.vertex.set1Value(0, ray_start_vec)
        self.ray_vtxs.vertex.set1Value(1, ray_end_vec)

        con_pick_action.apply(separator)
        picked_p_coords = SbVec3f(0.0, 0.0, 0.0)
        picked_point = con_pick_action.getPickedPoint()

        is_point_picked = False

        if (picked_point):
            picked_p_coords = picked_point.getPoint()
            self.sph_trans.translation.setValue(picked_p_coords)
            self.ray_vtxs.vertex.set1Value(1, picked_p_coords)
            is_point_picked = True

        # returning value seems to be safer
        return picked_point, picked_p_coords.getValue()

    def update_lever(self, x_lever_value, y_lever_value):
        self.buttons_state.lever_x = x_lever_value.current_state
        self.buttons_state.lever_y = y_lever_value.current_state
        self.logger.debug(
            "Controller %d X %.2f Y %.2f",
            self.iden,
            self.buttons_state.lever_x,
            self.buttons_state.lever_y)

    def update_grab(self, grab_value):
        self.buttons_state.grab = grab_value.current_state
        self.logger.debug(
            "Controller %d Grab %.2f",
            self.iden,
            self.buttons_state.grab)

    def get_local_q(self):
        qx = self.con_localtransform.rotation.getValue().getValue()[0]
        qy = self.con_localtransform.rotation.getValue().getValue()[1]
        qz = self.con_localtransform.rotation.getValue().getValue()[2]
        qw = self.con_localtransform.rotation.getValue().getValue()[3]
        return qx, qy, qz, qw

    def get_buttons_states(self):
        return self.buttons_state

    def read_file(self, filename):
        # Open the input file
        scene_input = SoInput()
        if not scene_input.openFile(filename):
            self.logger.warning("Cannot open file: %s", str(filename))
            return None

        # Read the whole file into the database
        graph = SoDB.readAll(scene_input)
        if graph is None:
            self.logger.warning("Problem reading file: %s", str(filename))
            return None

        scene_input.closeFile()
        return graph
