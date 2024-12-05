# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2023 Adrian Przekwas adrian.v.przekwas@gmail.com        *
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

from pivy.coin import SbVec3f, SbRotation
from pivy.coin import SoTransform
from dataclasses import dataclass

# only for key enums
from PySide.QtCore import Qt

# movement forced by keyboard input, float as some inertia implementation
# might be useful


@dataclass
class KeyboardMovement:
    walk: float = 0.0  # forward - backward
    sidestep: float = 0.0  # left - right
    xrot: float = 0.0  # pitch
    yrot: float = 0.0  # yaw
    zrot: float = 0.0  # roll


class xrMovement:
    def __init__(self, mov_type='ARCH'):
        self.movement_type = mov_type
        self.key_mov = KeyboardMovement()

    def set_movement_type(self, mov_type):
        self.movement_type = mov_type

    def transf_arch(self, hmdpos, hmdrot,
                    pri_con_inp, sec_con_inp,
                    mov_speed, rot_speed):
        prim_transf_mod = SoTransform()
        # *********************************************************************
        # Arch-like movement
        # analog stick/trackpad of the first controller
        # moves viewer up/down and left/right
        # analog stick/trackpad of the second controller
        # rotates viewer around center of the HMD and moves forward/backward
        # adjust self.primary_con and self.secondary_con to your prefereces
        # *********************************************************************
        qx = hmdrot.getValue()[0]
        qy = hmdrot.getValue()[1]
        qz = hmdrot.getValue()[2]
        qw = hmdrot.getValue()[3]
        # https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/index.htm
        mat02 = 2 * qx * qz + 2 * qy * qw
        mat22 = 1 - 2 * qx * qx - 2 * qy * qy
        z0 = mat02
        z2 = mat22
        # primary controller
        xaxis = pri_con_inp.lever_x
        yaxis = pri_con_inp.lever_y
        step = SbVec3f(0, yaxis * mov_speed, 0)
        step = step + SbVec3f(xaxis * z2 * mov_speed,
                              0,
                              -xaxis * z0 * mov_speed)
        prim_transf_mod.center.setValue(hmdpos)
        prim_transf_mod.translation.setValue(step)
        # secondary controller
        sec_transf_mod = SoTransform()
        xaxis = sec_con_inp.lever_x
        yaxis = sec_con_inp.lever_y
        step = SbVec3f(-yaxis * z0 * mov_speed,
                       0, -yaxis * z2 * mov_speed)
        sec_transf_mod.center.setValue(hmdpos)
        sec_transf_mod.translation.setValue(step)
        world_z_rot = SbRotation(SbVec3f(0, 1, 0), -xaxis)
        world_z_rot.scaleAngle(rot_speed)
        prim_transf_mod.rotation.setValue(world_z_rot)
        sec_transf_mod.combineLeft(prim_transf_mod)
        return sec_transf_mod

    def transf_free(self, pri_con_inp, sec_con_inp,
                    pri_con_local_transf,
                    sec_con_local_transf,
                    mov_speed, rot_speed):
        # *********************************************************************
        # Free movement:
        # analog stick/trackpad of the first (default left) controller
        # moves viewer forward or backward along the controller axis
        # analog stick/trackpad of the second (default right) controller
        # rotates viewer around center of the controller
        # *********************************************************************

        # primary controller
        prim_transf_mod = SoTransform()

        rot_pri = pri_con_local_transf.rotation.getValue()
        yaxis = pri_con_inp.lever_y

        z_move = SbVec3f(0, 0, yaxis)
        step = rot_pri.multVec(-z_move * mov_speed)
        prim_transf_mod.translation.setValue(step)

        # secondary controller
        sec_transf_mod = SoTransform()
        rot_sec = sec_con_local_transf.rotation.getValue()

        xaxis = sec_con_inp.lever_x
        yaxis = sec_con_inp.lever_y

        # stick moves world around one of controller axes
        con_x_rot = SbRotation(rot_sec.multVec(SbVec3f(1, 0, 0)), -yaxis)
        con_z_rot = SbRotation(rot_sec.multVec(SbVec3f(0, 0, 1)), -xaxis)

        sec_con_pos = sec_con_local_transf.translation.getValue()
        pad_rot = con_x_rot * con_z_rot
        pad_rot.scaleAngle(rot_speed)
        sec_transf_mod.center.setValue(sec_con_pos)
        sec_transf_mod.rotation.setValue(pad_rot)
        sec_transf_mod.combineLeft(prim_transf_mod)
        return sec_transf_mod

    def calculate_transformation(self, hmdpos, hmdrot,
                                 pri_con, sec_con,
                                 mov_speed, rot_speed):
        # transformation based on motion controllers input
        pri_con_inp = pri_con.get_buttons_states()
        sec_con_inp = sec_con.get_buttons_states()
        transf = SoTransform()
        if self.movement_type == 'ARCH':
            transf = self.transf_arch(hmdpos, hmdrot,
                                      pri_con_inp, sec_con_inp,
                                      mov_speed, rot_speed)
        elif self.movement_type == 'FREE':
            pri_con_local_transf = pri_con.get_local_transf()
            sec_con_local_transf = sec_con.get_local_transf()
            transf = self.transf_free(pri_con_inp, sec_con_inp,
                                      pri_con_local_transf,
                                      sec_con_local_transf,
                                      mov_speed, rot_speed)
        # additional transformation based on keyboard input
        transf_kb = SoTransform()
        rot_x = SbRotation(SbVec3f(1, 0, 0), self.key_mov.xrot * rot_speed)
        rot_y = SbRotation(SbVec3f(0, 1, 0), self.key_mov.yrot * rot_speed)
        rot_z = SbRotation(SbVec3f(0, 0, 1), self.key_mov.zrot * rot_speed)
        rot = rot_x * rot_y * rot_z
        transf_kb.rotation.setValue(rot)
        trsl = SbVec3f(self.key_mov.sidestep, 0, self.key_mov.walk) * mov_speed
        transf_kb.translation.setValue(trsl)
        transf.combineRight(transf_kb)
        return transf

    def key_pressed(self, key):
        # redefine keybindings here
        if (key == Qt.Key_Left):
            self.key_mov.yrot = 1.0
        if (key == Qt.Key_Right):
            self.key_mov.yrot = -1.0
        if (key == Qt.Key_Down):
            self.key_mov.xrot = -1.0
        if (key == Qt.Key_Up):
            self.key_mov.xrot = 1.0
        if (key == Qt.Key_U):
            self.key_mov.zrot = 1.0
        if (key == Qt.Key_O):
            self.key_mov.zrot = -1.0
        if (key == Qt.Key_K):
            self.key_mov.walk = 1.0
        if (key == Qt.Key_I):
            self.key_mov.walk = -1.0
        if (key == Qt.Key_L):
            self.key_mov.sidestep = 1.0
        if (key == Qt.Key_J):
            self.key_mov.sidestep = -1.0

    def key_released(self, key):
        if (key == Qt.Key_Left or Qt.Key_Right):
            self.key_mov.yrot = 0
        if (key == Qt.Key_Down or key == Qt.Key_Up):
            self.key_mov.xrot = 0
        if (key == Qt.Key_U or key == Qt.Key_O):
            self.key_mov.zrot = 0
        if (key == Qt.Key_K or key == Qt.Key_I):
            self.key_mov.walk = 0
        if (key == Qt.Key_L or key == Qt.Key_J):
            self.key_mov.sidestep = 0

    def reset_rot_axis(self, rot, axis):
        # resets rotation to given axis
        # useful when eg we want viewer standing normal to floor
        loc_axis = rot.multVec(axis)
        corr_rot = SbRotation(loc_axis, axis)
        rot = rot * corr_rot
        return rot
