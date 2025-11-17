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

import FreeCAD
import FreeCADGui

translate = FreeCAD.Qt.translate

# flag for rendering loop that it should read preferences
pref_updated = False

def reset_upd_flag():
    global pref_updated
    pref_updated = False

def preferences():
    return FreeCAD.ParamGet(
        "User parameter:BaseApp/Preferences/Mod/freecad-xr-workbench")

class PreferencesPage:
    def __init__(self, parent=None):
        self.form = FreeCADGui.PySideUic.loadUi(
            ":preferences/XRPreferences.ui")

    def saveSettings(self):
        pref = preferences()
        pref.SetInt("LinearSpeed", self.form.linearSpeedSlider.value())
        pref.SetInt("RotationalSpeed", self.form.rotSpeedSlider.value())
        pref.SetInt("AmbientLightIntesity", self.form.ambiLiSlider.value())
        pref.SetInt("DirectionalLightIntesity", self.form.dirLiSlider.value())
        msaa_vals = [0, 2, 4, 8]
        pref.SetInt("MSAA", msaa_vals[self.form.msaaComboBox.currentIndex()])
        pref.SetBool("MirrorEnable", self.form.mirrEnblCheckBox.isChecked())
        pref.SetBool("DebugEnable", self.form.debugEnblCheckBox.isChecked())
        pref.SetBool("UseHighestOpenXR", self.form.highestOpenxrCheckBox.isChecked())
        if self.form.movArchRadioButton.isChecked():
            pref.SetString("Movement", "ARCH")
        elif self.form.movFreeRadioButton.isChecked():
            pref.SetString("Movement", "FREE")
        pref.SetFloat("TPPCamXTransl", self.form.xTransSpinBox.value())
        pref.SetFloat("TPPCamYTransl", self.form.yTransSpinBox.value())
        pref.SetFloat("TPPCamZTransl", self.form.zTransSpinBox.value())
        pref.SetFloat("TPPCamXRot", self.form.xRotSpinBox.value())
        pref.SetFloat("TPPCamYRot", self.form.yRotSpinBox.value())
        pref.SetFloat("TPPCamZRot", self.form.zRotSpinBox.value())
        pref.SetFloat("TPPCamAngleRot", self.form.angleRotSpinBox.value())
        pref.SetFloat("TPPCamAspectW", self.form.aspectWSpinBox.value())
        pref.SetFloat("TPPCamAspectH", self.form.aspectHSpinBox.value())
        pref.SetFloat("TPPCamVFov", self.form.vertFovSpinBox.value())
        global pref_updated
        pref_updated = True


    def loadSettings(self):
        pref = preferences()
        self.form.linearSpeedSlider.setValue(pref.GetInt("LinearSpeed", 50))
        self.form.rotSpeedSlider.setValue(pref.GetInt("RotationalSpeed", 50))
        self.form.ambiLiSlider.setValue(
            pref.GetInt("AmbientLightIntesity", 40))
        self.form.dirLiSlider.setValue(
            pref.GetInt("DirectionalLightIntesity", 80))
        msaa_val_to_index = {0: 0, 2: 1, 4: 2, 8: 3}
        self.form.msaaComboBox.setCurrentIndex(msaa_val_to_index.get(pref.GetInt("MSAA", 4), 0))
        mov_str = pref.GetString("Movement", "ARCH")
        self.form.mirrEnblCheckBox.setChecked(pref.GetBool("MirrorEnable", False))
        self.form.debugEnblCheckBox.setChecked(pref.GetBool("DebugEnable", False))
        self.form.highestOpenxrCheckBox.setChecked(pref.GetBool("UseHighestOpenXR", False))
        self.form.xTransSpinBox.setValue(pref.GetFloat("TPPCamXTransl", 0.0))
        self.form.yTransSpinBox.setValue(pref.GetFloat("TPPCamYTransl", 0.0))
        self.form.zTransSpinBox.setValue(pref.GetFloat("TPPCamZTransl", 0.0))
        self.form.xRotSpinBox.setValue(pref.GetFloat("TPPCamXRot", 0.0))
        self.form.yRotSpinBox.setValue(pref.GetFloat("TPPCamYRot", 0.0))
        self.form.zRotSpinBox.setValue(pref.GetFloat("TPPCamZRot", 1.0))
        self.form.angleRotSpinBox.setValue(pref.GetFloat("TPPCamAngleRot", 0.0))
        # defaults based on Pi HQ camera, 6mm focal length
        self.form.aspectWSpinBox.setValue(pref.GetFloat("TPPCamAspectW", 6.29))
        self.form.aspectHSpinBox.setValue(pref.GetFloat("TPPCamAspectH", 4.71))
        self.form.vertFovSpinBox.setValue(pref.GetFloat("TPPCamVFov", 42.88))
        if mov_str == "ARCH":
            self.form.movArchRadioButton.setChecked(True)
        elif mov_str == "FREE":
            self.form.movFreeRadioButton.setChecked(True)

