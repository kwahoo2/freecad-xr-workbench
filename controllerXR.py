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

from pivy.coin import SoSeparator
from pivy.coin import SbVec3f, SbRotation
from pivy.coin import SoTransform
from pivy.coin import SoCube
from pivy.coin import SoInput, SoDB

class xrController:
    def __init__(self, iden = 0, log_level=logging.WARNING):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.controller_sep = SoSeparator() # this separator contains everything that moves with controller
        self.iden = iden
        self.con_transform = SoTransform()
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
        if (con_node == None):
            con_node = SoSeparator()
            con_cube = SoCube()
            con_cube.width.setValue(0.05)
            con_cube.height.setValue(0.025)
            con_cube.depth.setValue(0.15)
            con_node.addChild(con_cube) #  replace controller with simple cube if the iv file not found
        con_sep.addChild(self.con_transform)
        con_sep.addChild(con_node)
        self.controller_sep.addChild(con_sep)

    def get_controller_scenegraph(self):
        return self.controller_sep

    def update_pose(self, space_location):
        con_rot = SbRotation(space_location.pose.orientation.x,
                            space_location.pose.orientation.y,space_location.pose.orientation.z, space_location.pose.orientation.w)
        con_pos = SbVec3f(space_location.pose.position.x, space_location.pose.position.y,
                        space_location.pose.position.z)
        self.con_transform.rotation.setValue(con_rot)
        self.con_transform.translation.setValue(con_pos)
        self.con_transform.center.setValue(SbVec3f(0, 0, 0))

    def update_lever(self, x_lever_value, y_lever_value):
        x_axis = x_lever_value.current_state
        y_axis = y_lever_value.current_state
        self.logger.debug("Controller %d X %.2f Y %.2f", self.iden, x_axis, y_axis)

    def update_grab(self, grab_value):
        grab = grab_value.current_state
        self.logger.debug("Controller %d Grab %.2f", self.iden, grab)

    def read_file(self, filename):
        # Open the input file
        scene_input = SoInput()
        if not scene_input.openFile(filename):
            self.logger.warning("Cannot open file: %s", str(filename))
            return None

        # Read the whole file into the database
        graph = SoDB.readAll(scene_input)
        if graph == None:
            self.logger.warning("Problem reading file: %s", str(filename))
            return None

        scene_input.closeFile()
        return graph




