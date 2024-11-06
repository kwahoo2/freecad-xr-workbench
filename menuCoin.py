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
from pivy.coin import SoDirectionalLight

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
        text_rel_pos.translation.setValue(SbVec3f(-0.025, -0.007, 0.01))
        label = SoText3()
        text_scale = SoScale()
        text_scale.scaleFactor.setValue(SbVec3f(0.002, 0.002, 0.002))
        text_color = SoBaseColor()
        text_color.rgb = SbColor(1, 1, 1)
        self.button_sep.addChild(text_color)
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


class sliderWidget:
    def __init__(self, name="", text="", value=0.5):
        self.name = name
        self.value = value
        self.slider_sep = SoSeparator()
        self.relativ_loc = SoTransform()
        self.slider_sep.addChild(self.relativ_loc)
        self.back_color = SoBaseColor()
        self.back_color.rgb = SbColor(0.5, 0.5, 0.5)
        self.slider_sep.addChild(self.back_color)
        self.back_shape = SoCube()
        self.slider_width = 0.25
        self.back_shape.width.setValue(self.slider_width)
        self.back_shape.height.setValue(0.035)
        self.back_shape.depth.setValue(0.01)
        self.slider_sep.addChild(self.back_shape)

        # everything after this will be not pickable
        # useful for excluding the button label from picking
        unpickable = SoPickStyle()
        unpickable.style = SoPickStyle.UNPICKABLE
        self.slider_sep.addChild(unpickable)

        # moveable bar - unpickable (only background cube is pickable)
        # requires own separator, should not affect the text label
        bar_sep = SoSeparator()
        self.bar_rel_pos = SoTranslation()
        self.bar_rel_pos.translation.setValue(
            SbVec3f((value - 1) * 0.5 * self.slider_width, 0, 0.01))
        self.bar_shape = SoCube()
        self.bar_shape.width.setValue(self.slider_width * value)
        self.bar_shape.height.setValue(0.025)
        self.bar_shape.depth.setValue(0.01)
        bar_color = SoBaseColor()
        bar_color.rgb = SbColor(0, 1, 0)
        bar_sep.addChild(self.bar_rel_pos)
        bar_sep.addChild(bar_color)
        bar_sep.addChild(self.bar_shape)
        self.slider_sep.addChild(bar_sep)

        text_rel_pos = SoTranslation()
        text_rel_pos.translation.setValue(
            SbVec3f(-0.4 * self.slider_width, -0.007, 0.02))
        label = SoText3()
        text_scale = SoScale()
        text_scale.scaleFactor.setValue(SbVec3f(0.002, 0.002, 0.002))
        text_color = SoBaseColor()
        text_color.rgb = SbColor(1, 1, 1)
        self.slider_sep.addChild(text_color)
        label.string = text
        self.slider_sep.addChild(text_rel_pos)
        self.slider_sep.addChild(text_scale)
        self.slider_sep.addChild(label)

    def set_location(self, pos, rot):
        self.relativ_loc.translation = pos
        self.relativ_loc.rotation = rot

    def set_value(self, value):
        # value can be 0 - 1
        self.value = value
        self.bar_rel_pos.translation.setValue(
            SbVec3f((value - 1) * 0.5 * self.slider_width, 0, 0.01))
        self.bar_shape.width.setValue(self.slider_width * value)

    def get_scenegraph(self):
        return self.slider_sep

    def get_widget_tail(self):
        return self.back_shape


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
        # for better menu visibility
        light = SoDirectionalLight()
        light.direction.setValue(-1, -1, -1)
        light.intensity.setValue(0.5)
        self.menu_node.addChild(light)
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

        self.lin_speed_slider = sliderWidget(
            "lin_speed_slider", "Linear Speed")
        self.lin_speed_slider.set_location(
            SbVec3f(
                0.0, 0.15, -0.3), SbRotation(
                0, 0, 0, 0))
        self.menu_node.addChild(self.lin_speed_slider.get_scenegraph())
        self.widget_list.append(self.lin_speed_slider)

        self.rot_speed_slider = sliderWidget(
            "rot_speed_slider", "Rotational Speed")
        self.rot_speed_slider.set_location(
            SbVec3f(
                0.0, 0.2, -0.3), SbRotation(
                0, 0, 0, 0))
        self.menu_node.addChild(self.rot_speed_slider.get_scenegraph())
        self.widget_list.append(self.rot_speed_slider)

    def update_location(self, pos, rot):
        self.location.translation = pos
        self.location.rotation = rot

    def get_menu_scenegraph(self):
        return self.menu_sep

    def show_menu(self):
        self.menu_node.whichChild = SO_SWITCH_ALL

    def hide_menu(self):
        self.menu_node.whichChild = SO_SWITCH_NONE

    def find_picked_widget(self, tail, coords):
        widget = None
        for w in self.widget_list:
            if (w.get_widget_tail() == tail):
                widget = w
        if isinstance(widget, buttonWidget):
            # buttons can be grouped in radio button groups
            # then all buttons have to be deselected except the picked one
            # radio group 0 means that button is independent
            radio_group = widget.radio_group
            if radio_group > 0:
                for w in self.widget_list:
                    if isinstance(w, buttonWidget):
                        if (w.radio_group == radio_group):
                            w.select(False)
            widget.select(True)
        elif isinstance(widget, sliderWidget):
            # u texture value is used as slider value
            widget.set_value(coords[0])
        return widget

    def select_widget_by_name(self, name, value=0):
        widget = None
        for w in self.widget_list:
            if (w.name == name):
                widget = w
        if isinstance(widget, buttonWidget):
            radio_group = widget.radio_group
            if radio_group > 0:
                for w in self.widget_list:
                    if isinstance(w, buttonWidget):
                        if (w.radio_group == radio_group):
                            w.select(False)
            widget.select(True)
        elif isinstance(widget, sliderWidget):
            widget.set_value(value)