# FreeCAD XR Workbench

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.

[Forum thread](https://forum.freecad.org/viewtopic.php?t=39526)

# This is a branch for making mixed reality videos

The HMD mirror view is replaced by a view generated with tracked third person camera.

![FreeCAD-XR][fcxr]

[fcxr]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/tpp-cam/.github/images/fcxr-screen.png "View of active workbench"


## Prerequisites

### Special requirements for this branch

The camera tracker should be set to the "Camera" role.

Adjust the camera geometry in the `commonXR.py`:

```
        self.tppcamera.heightAngle.setValue(42.88 * pi / 180)
        self.tppcamera.aspectRatio.setValue(6.29 / 4.71) 
```

Adjust camera to tracker relative location:

```
        # adjust camera to tracker rotation - OpenXR coordinates (Y vertical)
        cam_tracker_rot = SbRotation(SbVec3f(0, 1, 0), pi)
        # adjust camera to tracker translation - OpenXR coordinates (meters)
        cam_tracker_transl = SbVec3f(0.034, -0.033, 0)
```

### Software Dependencies

* FreeCAD 0.20 or later
* Python 3.11+
* an OpenXR Runtime, it can be selected manually with:

`XR_RUNTIME_JSON=json_file_placement FreeCAD_executable`

an example:

`XR_RUNTIME_JSON=/usr/local/share/openxr/1/openxr_monado.json ./FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage`

Note: the OpenXR has to support [XR_KHR_opengl_enable](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XR_KHR_opengl_enable.html) extension. Known runtimes that support this extension include SteamVR and Monado.

#### Python libraries

* pyopenxr
* PyOpenGL

Installation of the libraries:

* Linux: `pip install pyopenxr`
* Windows: navigate to the `FreeCAD_xxx/bin` directory and run: `python.exe -m pip install pyopenxr`

### Hardware

* Any HMD supported by OpenXR (HTC Vive, Valve Index, Oculus Rift, or a Windows Mixed Reality headset)

## Installation and Usage

Copy the `freecad-xr-workbench` directory to FreeCAD's `Mod` directory:

* Linux `/home/username/.FreeCAD/Mod/` (can be `/home/username/.local/share/FreeCAD/Mod/` in old releases)
* Windows `%APPDATA%\FreeCAD\Mod\`, which is usually `C:\Users\username\Appdata\Roaming\FreeCAD\Mod\`

See also: [FreeCAD Wiki: Installing more workbenches](https://wiki.freecad.org/Installing_more_workbenches)

A new `XR` workbench will appear.

## Movement in the 3D space

The XR workbench can use two motion controllers to introduce artificial movement on top of the room-scale (real world) movement. There are two modes (select one in Edit->Preferences->XRWorkbench):

### Arch-like movement:
* analog stick/trackpad of the primary (default left) controller moves viewer up/down and left/right,
* analog stick/trackpad of the secondary (default right) controller rotates viewer around center of the HMD and moves forward/backward.

### Free movement:
* analog stick/trackpad of the primary (default left) controller moves viewer forward or backward along the controller axis,
* analog stick/trackpad of the secondary (default right) controller rotates viewer around center of the controller.

Additionally, a teleport movement is available: press secondary (default right) controller trigger, a ray become visible. Release the trigger, you will be teleported to place where the ray was intersecting (indicated by a small sphere) an object.

## Known issues:

Wayland/EGL support not implemented yet.

## Tips and tricks:

Linux specific:

SteamVR performance can be abysmal, it is often much better with Monado.
However, running Monado with libsurvive using multiple Lighthouses can cause bad tracking.
Fortunately, there is a way to combine the best of both world - use Monado with SteamVR tracking:

`STEAMVR_LH_ENABLE=true monado-service`

## License

Check [LICENSE](LICENSE) for details.
