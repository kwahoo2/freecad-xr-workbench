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

class XRWorkbench (Workbench):
    def __init__(self):
        self.__class__.MenuText = "XR"
        self.__class__.ToolTip = "XR workbench"
        self.__class__.Icon = """
/* XPM */
static char * glasses_xpm[] = {
"16 16 7 1",
" 	c None",
".	c #000000",
"+	c #010101",
"@	c #030303",
"#	c #020202",
"$	c #010100",
"%	c #020302",
"                ",
"       ..       ",
"     ..++.      ",
"  .@+++  .      ",
"++.+            ",
"+++..           ",
"...++#.        .",
"....+....    @##",
"....+ $..+%@### ",
".+..+ +....##   ",
" .++  ......    ",
"      .....     ",
"      .....     ",
"       .+.      ",
"                ",
"                "};
"""

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        import startXR, stopXR, enableMirror, disableMirror # import here all the needed files that create your FreeCAD commands
        self.list = ["startXR", "stopXR", "enableMirror", "disableMirror"] # a list of command names created in the line above
        self.appendToolbar("XR viewer", self.list) # creates a new toolbar with your commands
        self.appendMenu("XR menu", self.list) # creates a new menu
        # self.appendMenu(["An existing Menu", "My submenu"], self.list) # appends a submenu to an existing menu

    def Activated(self):
        """This function is executed whenever the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("XR commands", self.list) # add commands to the context menu

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

Gui.addWorkbench(XRWorkbench())
