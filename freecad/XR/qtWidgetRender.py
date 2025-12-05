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

import FreeCADGui as Gui

from PySide.QtWidgets import QApplication, QDockWidget
from PySide.QtGui import QImage, QPainter, qGray, qRed, qGreen, qBlue, qAlpha, QMouseEvent
from PySide.QtCore import Qt, QPoint, QTimer, QObject, SIGNAL
from math import pi
import numpy as np

from pivy.coin import SoSeparator
from pivy.coin import SoSwitch, SO_SWITCH_NONE, SO_SWITCH_ALL
from pivy.coin import SoCoordinate3, SoIndexedFaceSet
from pivy.coin import SoTransform
from pivy.coin import SO_END_FACE_INDEX
from pivy.coin import SoTexture2, SoSFImage, SoTextureCoordinate2
from pivy.coin import SbVec2s, SbVec3f, SbRotation
from pivy.coin import SoLightModel, SoPickStyle

# renders Qt widgets as face textures in the Coin3D scene

widget_update_interval = 0

class qtWidgetRender:
    def __init__(self, name,
                 pos=SbVec3f(0.0, 0.0, -2.0), scale=0.002):
        self.widget_sep = SoSeparator()

        # 2D Qt widget preview
        self.widget = self.find_widget_by_name(name)
        if not self.widget:
            return
        self.qt_widget_sep = SoSwitch()
        self.qt_widget_sep.whichChild = SO_SWITCH_NONE
        self.widget_sep.addChild(self.qt_widget_sep)

        # render without shading (full bright)
        light_model = SoLightModel()
        light_model.model = SoLightModel.BASE_COLOR
        self.qt_widget_sep.addChild(light_model)

        # the widget's face should be pickable
        pickable = SoPickStyle()
        pickable.style = SoPickStyle.SHAPE
        self.qt_widget_sep.addChild(pickable)

        # face to show rendered image
        self.widget_transform = SoTransform()
        self.qt_widget_sep.addChild(self.widget_transform)

        # explicit definition is required,
        # otherwise Coin3D would rotate texture 90 deg height > width
        tex_coords = SoTextureCoordinate2()
        tex_coords.point.setValues([
            (0, 0),
            (1, 0),
            (1, 1),
            (0, 1)
        ])
        self.qt_widget_sep.addChild(tex_coords)

        self.widget_face_coords = SoCoordinate3()
        self.qt_widget_sep.addChild(self.widget_face_coords)
        self.face_set = SoIndexedFaceSet()
        self.face_set.coordIndex.setValues(
            0, 5, [0, 1, 2, 3, SO_END_FACE_INDEX])
        self.qt_widget_sep.addChild(self.face_set)

        # add a texture
        self.texture = SoTexture2()
        self.qt_widget_sep.insertChild(self.texture, 1)
        self.sosf_img = SoSFImage()
        self.widget_rendered = False

        # place widget in 3D space
        self.update_widget_transf(pos, SbRotation(SbVec3f(0, 0, 1), 0))
        self.scale = scale
        self.set_widget_face_size()

        # widget rendering is slow and should be performed asynchronously
        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        QObject.connect(
            self.render_timer,
            SIGNAL("timeout()"),
            self.render_widget)

    def find_widget_by_name(self, name):  # eg. Model (QDockWidget) - tree view
        mw = Gui.getMainWindow()
        # find Model (QDockWidget)
        dock_widget = mw.findChild(QDockWidget, name)
        if not dock_widget:
            print(f"Qt Widget not found: {name}")
            return None

        inner_widget = dock_widget.widget()
        if not inner_widget:
            print(f"No widget found inside the {name}")
            return None

        return inner_widget

    def get_scenegraph(self):
        return self.widget_sep

    def get_widget_tail(self):
        return self.face_set

    def show_widget(self):
        self.qt_widget_sep.whichChild = SO_SWITCH_ALL
        self.render_timer.start(widget_update_interval)

    def hide_widget(self):
        self.qt_widget_sep.whichChild = SO_SWITCH_NONE

    def toggle_widget(self):
        if self.qt_widget_sep.whichChild.getValue() == SO_SWITCH_NONE:
            self.show_widget()
        else:
            self.hide_widget()

    def update_widget_transf(self, pos=None, rot=None):
        if pos:
            self.widget_transform.translation.setValue(pos)
        if rot:
            self.widget_transform.rotation.setValue(rot)

    def set_widget_face_size(self):
        w = self.widget.size().width() * self.scale
        h = self.widget.size().height() * self.scale
        self.widget_face_coords.point.set1Value(0, -w / 2, -h / 2, 0)
        self.widget_face_coords.point.set1Value(1, w / 2, -h / 2, 0)
        self.widget_face_coords.point.set1Value(2, w / 2, h / 2, 0)
        self.widget_face_coords.point.set1Value(3, -w / 2, h / 2, 0)

    def render_widget(self):
        # inspired by:
        # https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Draft/draftutils/gui_utils.py
        # cam be expensive, so run it asynchronously

        if self.qt_widget_sep.whichChild.getValue() == SO_SWITCH_NONE:
            return
        if not self.widget:
            return

        self.set_widget_face_size()
        image = QImage(self.widget.size(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self.widget.render(painter, QPoint(0, 0))
        painter.end()

        ptr = image.constBits()
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((image.height(), image.width(), 4))

        # reverse rows, because 0,0 is in left-top for Qt and left-bottom for GL
        arr = arr[::-1, :, :]

        byte_list = arr.tobytes()
        size = SbVec2s(image.width(), image.height())
        numcomponents = 4 # RGBA
        self.sosf_img.setValue(size, numcomponents, byte_list)
        self.widget_rendered = True

    def swap_texture(self):
        if self.qt_widget_sep.whichChild.getValue() == SO_SWITCH_NONE:
            return
        if self.widget_rendered:
            self.texture.image = self.sosf_img
            self.widget_rendered = False
            self.render_timer.start(widget_update_interval)

    def project_click(self, tex_coords):
        if not self.widget:
            return
        s = self.widget.size()
        u_widget = int(s.width() * tex_coords[0])
        v_widget = int(s.height() * (1 - tex_coords[1]))

        pos = QPoint(u_widget, v_widget)
        glo_pos = self.widget.mapToGlobal(pos)
        target_widget = self.widget.childAt(pos)
        if target_widget:
            pos_on_target = target_widget.mapFromGlobal(glo_pos)
            press_event = QMouseEvent(
                QMouseEvent.MouseButtonPress,
                pos_on_target,
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            )
            QApplication.sendEvent(target_widget, press_event)

            release_event = QMouseEvent(
                QMouseEvent.MouseButtonRelease,
                pos_on_target,
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            )
            QApplication.sendEvent(target_widget, release_event)
