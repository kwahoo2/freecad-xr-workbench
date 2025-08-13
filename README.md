# FreeCAD XR Workbench

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.
More in [Extending Workbench](doc/Extending_Workbench.md).

[Forum thread](https://forum.freecad.org/viewtopic.php?t=39526)

![FreeCAD-XR][fcxr]

[fcxr]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/fcxr-screen.png "View of active workbench"

## Prerequisites

### Software Dependencies

* FreeCAD 0.20 or later, some features require FreeCAD 1.1 (dev)
* Python 3.11+
* an OpenXR Runtime (eg. SteamVR 2.11.2 or later, Monado), it can be selected manually with:

`XR_RUNTIME_JSON=json_file_placement FreeCAD_executable`

an example:

`XR_RUNTIME_JSON=/usr/local/share/openxr/1/openxr_monado.json ./FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage`

Note: the OpenXR has to support [XR_KHR_opengl_enable](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XR_KHR_opengl_enable.html) extension. List of runtimes that support this extension [can be found here.](https://github.khronos.org/OpenXR-Inventory/extension_support.html#XR_KHR_opengl_enable)



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

### Keyboard input
If motion controllers are unavailable, a keyboard can be used.

| Keys             | Move type       |
| ---------------- | ----------------|
| Up/Down Arrows   | Pitch           |
| Left/Right Arrows| Yaw             |
| U/O              | Roll            |
| I/K              | Forward/Backward|
| J/L              | Left/Right      |
| PageUp/PageDown  | Up/Down         |

Depending on platform, the mirror window may or may not need to be shown and focused (click into to focus) to catch keys.

## Dragging objects and modelling tools
Dragging objects with the motion controller ray is available since 15.12.2024 (39642) FreeCAD 1.1 (dev) Weekly Build.

This version is also required for modelling tools like a [Pad or Pocket.](https://youtu.be/BlZWMUpZ5mU)

## Tips and tricks:

SteamVR:

SteamVR checks the proximity sensor in the HMD, so the user must wear the HMD fully to enable rendering. Only if the head is detected the runtime will return XR_SESSION_STATE_FOCUSED required for rendering. The sensor is located in the middle of the HMD, between (slightly above) the lenses in most HMDs.

Linux specific:

Monado with libsurvive works well, including two Lighthouses setup.
In cause of issues with libsurvive tracking, Monado can use SteamVR tracking:

`STEAMVR_LH_ENABLE=true monado-service`

Wayland:

Pure Wayland/EGL session may need additional steps, please check [EGL Howto](doc/EGL_Howto.md)

## License

Check [LICENSE](LICENSE) for details.
