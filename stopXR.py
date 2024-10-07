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

import os

import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP

import commonXR as cxr


class XR_Stop():
    """A command closing the XR viewer"""

    def GetResources(self):
        return {
            "Pixmap": "Glasses_disabled.svg",
            "Accel": "X,C",  # a default shortcut (optional)
            "MenuText": QT_TRANSLATE_NOOP("XR_Stop", "Close XR viewer"),
            "ToolTip": QT_TRANSLATE_NOOP("XR_Stop", "Stops rendering in VR HMD")}

    def Activated(self):
        cxr.close_xr_viewer()
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True  # True or False


Gui.addCommand("stopXR", XR_Stop())
