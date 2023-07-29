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

import commonXR as cxr

class XR_Viewer():
    """A command opening the XR viewer"""
    def __init__(self):
        self.xr_dock_w = None # XR docked window and OpenXR rendering object

    def GetResources(self):
        return {
            "Pixmap": os.path.join(
                os.path.dirname(__file__), "icons", "Stepien_Glasses.svg"
            ),
            "Accel"   : "X,R", # a default shortcut (optional)
            "MenuText": "Open XR viewer",
            "ToolTip" : "Starts rendering in VR HMD"}

    def Activated(self):
        cxr.open_xr_viewer()
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True # True or False

Gui.addCommand("startXR", XR_Viewer())
