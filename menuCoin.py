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

from pivy.coin import SoSeparator
from pivy.coin import SoTransform, SoTranslation, SoScale
from pivy.coin import SbVec3f, SbRotation
from pivy.coin import SoSwitch, SoPickStyle, SO_SWITCH_NONE, SO_SWITCH_ALL
from pivy.coin import SoCube, SoText3
from pivy.coin import SoBaseColor, SbColor
from pivy.coin import SoEnvironment

color_notsel = SbColor(0.5, 0.5, 0.5)
color_select = SbColor(0, 1, 0)


class buttonWidget:
    def __init__(self, name="", text="", radio_group=0):
        self.name = name
        self.radio_group = radio_group
        self.button_sep = SoSeparator()
        # location relative to hand
        self.relativ_loc = SoTransform()
        self.button_sep.addChild(self.relativ_loc)
        self.button_color = SoBaseColor()
        self.button_color.rgb = color_notsel
        self.button_sep.addChild(self.button_color)
        self.button_shape = SoCube()
        self.button_shape.width.setValue(0.08)
        self.button_shape.height.setValue(0.035)
        self.button_shape.depth.setValue(0.01)
        self.button_sep.addChild(self.button_shape)

        # everything after this will be not pickable
        # useful for excluding the button label from picking
        unpickable = SoPickStyle()
        unpickable.style = SoPickStyle.UNPICKABLE
        self.button_sep.addChild(unpickable)
        text_rel_pos = SoTranslation()
        text_rel_pos.translation.setValue(SbVec3f(-0.025, -0.005, 0.01))
        label = SoText3()
        text_scale = SoScale()
        text_scale.scaleFactor.setValue(SbVec3f(0.002, 0.002, 0.002))
        text_color = SoBaseColor()
        text_color.rgb = SbColor(1, 1, 1)
        self.button_sep.addChild(text_color)
        # ambient lighting makes text readable everywhere
        se = SoEnvironment()
        se.ambientIntensity.setValue(0.8)
        self.button_sep.addChild(se)
        label.string = text
        self.button_sep.addChild(text_rel_pos)
        self.button_sep.addChild(text_scale)
        self.button_sep.addChild(label)

    def set_location(self, pos, rot):
        self.relativ_loc.translation = pos
        self.relativ_loc.rotation = rot

    def select(self, selected):
        if selected:
            self.button_color.rgb = color_select
        else:
            self.button_color.rgb = color_notsel

    def get_scenegraph(self):
        return self.button_sep

    def get_widget_tail(self):
        return self.button_shape


class coinMenu:
    def __init__(self, visible=False):
        self.widget_list = []
        self.menu_sep = SoSeparator()
        self.menu_node = SoSwitch()
        if visible:
            self.menu_node.whichChild = SO_SWITCH_ALL
        else:
            self.menu_node.whichChild = SO_SWITCH_NONE
        self.menu_sep.addChild(self.menu_node)
        # location copied from hand
        self.location = SoTransform()
        self.menu_node.addChild(self.location)
        self.free_mov_button = buttonWidget("free_mov_button", "Free", 1)
        # set location relative to menu
        self.free_mov_button.set_location(
            SbVec3f(-0.05, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.menu_node.addChild(self.free_mov_button.get_scenegraph())
        self.widget_list.append(self.free_mov_button)

        # button in radio group 1
        self.arch_mov_button = buttonWidget("arch_mov_button", "Arch", 1)
        self.arch_mov_button.set_location(
            SbVec3f(
                0.05, 0.1, -0.3), SbRotation(
                0, 0, 0, 0))
        self.menu_node.addChild(self.arch_mov_button.get_scenegraph())
        self.widget_list.append(self.arch_mov_button)

    def update_location(self, pos, rot):
        self.location.translation = pos
        self.location.rotation = rot

    def get_menu_scenegraph(self):
        return self.menu_sep

    def show_menu(self):
        self.menu_node.whichChild = SO_SWITCH_ALL

    def hide_menu(self):
        self.menu_node.whichChild = SO_SWITCH_NONE

    def find_picked_widget(self, tail):
        widget = None
        for w in self.widget_list:
            if (w.get_widget_tail() == tail):
                widget = w
        if widget:
            # buttons can be grouped in radio button groups
            # then all buttons have to be deselected except the picked one
            # radio group 0 means that button is independent
            radio_group = widget.radio_group
            if radio_group > 0:
                for w in self.widget_list:
                    if (w.radio_group == radio_group):
                        w.select(False)
            widget.select(True)
        return widget

    def select_widget_by_name(self, name):
        widget = None
        for w in self.widget_list:
            if (w.name == name):
                widget = w
        if widget:
            radio_group = widget.radio_group
            if radio_group > 0:
                for w in self.widget_list:
                    if (w.radio_group == radio_group):
                        w.select(False)
            widget.select(True)
