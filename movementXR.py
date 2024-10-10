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


class xrMovement:
    def __init__(self, mov_type='ARCH'):
        self.movement_type = mov_type

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
        qx = pri_con_local_transf.rotation.getValue().getValue()[0]
        qy = pri_con_local_transf.rotation.getValue().getValue()[1]
        qz = pri_con_local_transf.rotation.getValue().getValue()[2]
        qw = pri_con_local_transf.rotation.getValue().getValue()[3]

        xaxis = pri_con_inp.lever_x
        yaxis = pri_con_inp.lever_y

        mat02 = 2 * qx * qz + 2 * qy * qw
        mat12 = 2 * qy * qz - 2 * qx * qw
        mat22 = 1 - 2 * qx * qx - 2 * qy * qy

        step = SbVec3f(-yaxis * mat02 * mov_speed,
                       -yaxis * mat12 * mov_speed,
                       -yaxis * mat22 * mov_speed)
        prim_transf_mod.translation.setValue(step)

        # secondary controller
        sec_transf_mod = SoTransform()
        qx = sec_con_local_transf.rotation.getValue().getValue()[0]
        qy = sec_con_local_transf.rotation.getValue().getValue()[1]
        qz = sec_con_local_transf.rotation.getValue().getValue()[2]
        qw = sec_con_local_transf.rotation.getValue().getValue()[3]

        xaxis = sec_con_inp.lever_x
        yaxis = sec_con_inp.lever_y

        mat00 = 1 - 2 * qy * qy - 2 * qz * qz
        mat02 = 2 * qx * qz + 2 * qy * qw
        mat10 = 2 * qx * qy + 2 * qz * qw
        mat12 = 2 * qy * qz - 2 * qx * qw
        mat20 = 2 * qx * qz - 2 * qy * qw
        mat22 = 1 - 2 * qx * qx - 2 * qy * qy

        con_x_axis = SbVec3f(mat00, mat10, mat20)
        con_z_axis = SbVec3f(mat02, mat12, mat22)
        # stick moves world around one of controller axes
        con_x_rot = SbRotation(con_x_axis, -yaxis)
        con_z_rot = SbRotation(con_z_axis, -xaxis)

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
        pri_con_inp = pri_con.get_buttons_states()
        sec_con_inp = sec_con.get_buttons_states()
        if self.movement_type == 'ARCH':
            return self.transf_arch(hmdpos, hmdrot,
                                    pri_con_inp, sec_con_inp,
                                    mov_speed, rot_speed)
        elif self.movement_type == 'FREE':
            pri_con_local_transf = pri_con.get_local_transf()
            sec_con_local_transf = sec_con.get_local_transf()
            return self.transf_free(pri_con_inp, sec_con_inp,
                                    pri_con_local_transf,
                                    sec_con_local_transf,
                                    mov_speed, rot_speed)
        else:
            return SoTransform()
