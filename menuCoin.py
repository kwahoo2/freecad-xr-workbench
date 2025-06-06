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
    def __init__(self, name="", text="", radio_group=0, width=0.08):
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
        self.button_shape.width.setValue(width)
        self.button_shape.height.setValue(0.035)
        self.button_shape.depth.setValue(0.01)
        self.button_sep.addChild(self.button_shape)

        # everything after this will be not pickable
        # useful for excluding the button label from picking
        unpickable = SoPickStyle()
        unpickable.style = SoPickStyle.UNPICKABLE
        self.button_sep.addChild(unpickable)
        text_rel_pos = SoTranslation()
        text_rel_pos.translation.setValue(SbVec3f(-0.4 * width, -0.007, 0.01))
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
    def __init__(self, name="", text="", value=0.5, width=0.25):
        self.name = name
        self.value = value
        self.slider_sep = SoSeparator()
        self.relativ_loc = SoTransform()
        self.slider_sep.addChild(self.relativ_loc)
        self.back_color = SoBaseColor()
        self.back_color.rgb = SbColor(0.5, 0.5, 0.5)
        self.slider_sep.addChild(self.back_color)
        self.back_shape = SoCube()
        self.slider_width = width
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

class labelWidget:
    def __init__(self, name="", text="", width=0.08):
        self.name = name
        self.label_sep = SoSeparator()
        self.relativ_loc = SoTransform()
        self.label_sep.addChild(self.relativ_loc)

        # everything after this will be not pickable
        # useful for excluding the label label from picking
        unpickable = SoPickStyle()
        unpickable.style = SoPickStyle.UNPICKABLE
        self.label_sep.addChild(unpickable)
        text_rel_pos = SoTranslation()
        text_rel_pos.translation.setValue(SbVec3f(-0.4 * width, -0.007, 0.01))
        self.label = SoText3()
        text_scale = SoScale()
        text_scale.scaleFactor.setValue(SbVec3f(0.002, 0.002, 0.002))
        text_color = SoBaseColor()
        text_color.rgb = SbColor(0, 0.2, 0)
        self.label_sep.addChild(text_color)
        self.label.string = text
        self.label_sep.addChild(text_scale)
        self.label_sep.addChild(self.label)

    def set_location(self, pos, rot):
        self.relativ_loc.translation = pos
        self.relativ_loc.rotation = rot

    def set_text(self, text):
        self.label.string = text

    def get_scenegraph(self):
        return self.label_sep

    def get_widget_tail(self):
        return None # not required, since it is never picked


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

    def update_location(self, pos, rot):
        self.location.translation = pos
        self.location.rotation = rot

    def get_menu_scenegraph(self):
        return self.menu_sep

    def show_menu(self):
        self.menu_node.whichChild = SO_SWITCH_ALL

    def hide_menu(self):
        self.menu_node.whichChild = SO_SWITCH_NONE

    def is_hidden(self):
        if (self.menu_node.whichChild.getValue() == SO_SWITCH_NONE):
            return True
        else:
            return False

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

# this is the main menu
class mainCoinMenu(coinMenu):
    def __init__(self, visible=False):
        super().__init__(visible)

        # buttons in radio group 1
        self.free_mov_button = buttonWidget("free_mov_button", "Free", 1)
        # set location relative to menu
        self.free_mov_button.set_location(
            SbVec3f(-0.05, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.free_mov_button)

        self.arch_mov_button = buttonWidget("arch_mov_button", "Arch", 1)
        self.arch_mov_button.set_location(
            SbVec3f(
                0.05, 0.1, -0.3), SbRotation(
                0, 0, 0, 0))
        self.widget_list.append(self.arch_mov_button)

        self.lin_speed_slider = sliderWidget(
            "lin_speed_slider", "Linear Speed")
        self.lin_speed_slider.set_location(
            SbVec3f(
                0.0, 0.15, -0.3), SbRotation(
                0, 0, 0, 0))
        self.widget_list.append(self.lin_speed_slider)

        self.rot_speed_slider = sliderWidget(
            "rot_speed_slider", "Rotational Speed")
        self.rot_speed_slider.set_location(
            SbVec3f(
                0.0, 0.2, -0.3), SbRotation(
                0, 0, 0, 0))
        self.widget_list.append(self.rot_speed_slider)

        self.scale_slider = sliderWidget(
            "scale_slider", "Model Scale")
        self.scale_slider.set_location(
            SbVec3f(
                0.0, 0.25, -0.3), SbRotation(
                0, 0, 0, 0))
        self.widget_list.append(self.scale_slider)

        # buttons in radio group 2
        self.teleport_mode_button = buttonWidget(
            "teleport_mode_button", "Teleport Mode", 2, 0.2)
        self.teleport_mode_button.set_location(
            SbVec3f(0.25, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.teleport_mode_button)

        self.line_builder_button = buttonWidget(
            "line_builder_button", "Line Builder", 2, 0.2)
        self.line_builder_button.set_location(
            SbVec3f(0.25, 0.05, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.line_builder_button)

        self.cube_builder_button = buttonWidget(
            "cube_builder_button", "Cube Builder", 2, 0.2)
        self.cube_builder_button.set_location(
            SbVec3f(0.25, 0, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.cube_builder_button)

        self.working_plane_button = buttonWidget(
            "working_plane_button", "Working Plane", 2, 0.2)
        self.working_plane_button.set_location(
            SbVec3f(0.5, 0.05, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.working_plane_button)

        # no radio group
        self.toggle_plane_button = buttonWidget(
            "toggle_plane_button", "Toggle Plane", 0, 0.2)
        self.toggle_plane_button.set_location(
            SbVec3f(0.5, 0.0, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.toggle_plane_button)

        # add Coin3D representation of every widget
        for w in self.widget_list:
            self.menu_node.addChild(w.get_scenegraph())

    def add_picking_buttons(self):
        # these buttons are used to select picking and dragging object modes with a ray
        # radio group 2
        self.pick_sel_button = buttonWidget(
            "pick_sel_button", "Selection Mode", 2, 0.2)
        self.pick_sel_button.set_location(
            SbVec3f(0.25, -0.05, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.pick_sel_button)
        self.menu_node.addChild(self.pick_sel_button.get_scenegraph())

        self.pick_drag_button = buttonWidget(
            "pick_drag_button", "Dragging Mode", 2, 0.2)
        self.pick_drag_button.set_location(
            SbVec3f(0.25, -0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.pick_drag_button)
        self.menu_node.addChild(self.pick_drag_button.get_scenegraph())

# this is menu for editing objects
class editCoinMenu(coinMenu):
    def __init__(self, visible=False):
        super().__init__(visible)

        self.del_obj_button = buttonWidget("del_obj_button", "Delete object", 0, 0.2)
        # set location relative to menu location
        self.del_obj_button.set_location(
            SbVec3f(-0.05, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.del_obj_button)

        self.new_body_button = buttonWidget("new_body_button", "Create a body", 0, 0.2)
        self.new_body_button.set_location(
            SbVec3f(0.45, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.new_body_button)

        self.close_button = buttonWidget("close_button", "Close menu", 0, 0.2)
        self.close_button.set_location(
            SbVec3f(-0.05, 0.2, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.close_button)

        # buttons in radio group 1
        self.pad_button = buttonWidget("pad_button", "Pad", 1)
        self.pad_button.set_location(
            SbVec3f(0.15, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.pad_button)

        self.pocket_button = buttonWidget("pocket_button", "Pocket", 1)
        self.pocket_button.set_location(
            SbVec3f(0.25, 0.1, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.pocket_button)

        self.label = labelWidget("label", "Pocket", 0.2)
        self.label.set_location(
            SbVec3f(-0.05, 0.3, -0.3), SbRotation(0, 0, 0, 0))
        self.widget_list.append(self.label)

        for w in self.widget_list:
            self.menu_node.addChild(w.get_scenegraph())

    def update_label(self, text):
        self.label.set_text(text)
