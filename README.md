# Virtual Reality

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.
More in [Extending Workbench](Resources/doc/Extending_Workbench.md).

[Forum thread](https://forum.freecad.org/viewtopic.php?t=39526)

![FreeCAD-XR][fcxr]

[fcxr]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/fcxr-screen.png "View of active workbench"

## Demo video

[![FreeCAD Virtual Reality Addon](https://img.youtube.com/vi/6aVT2NHf4vE/0.jpg)](https://youtu.be/6aVT2NHf4vE)

## Prerequisites

### Software Dependencies

* FreeCAD 1.1rc1
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

A new `Virtual Reality` workbench will appear.

## Movement in the 3D space

The Virtual Reality workbench can use two motion controllers to introduce artificial movement on top of the room-scale (real world) movement. There are two modes (select one in Edit->Preferences->Virtual Reality):

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

## Controller menus
Pressing the left controller trigger shows the main options and tools menu. The current tool can be selected by pointing the ray and releasing the trigger. The selected tool affects the right controller behavior. Currently available tools:

* Teleport Mode – enables teleport movement. Point the right controller ray at the destination surface and press its trigger. You will be teleported to the new destination.
* Line Builder – allows building polylines in 3D space. If a polyline is created on a flat plane and closed, it will be converted to a face. You may use the Working Plane tool as a plane for drawing polylines. Press the left controller trigger to finish polyline creation. You may also adjust the picking radius (using a slider in the same menu) for easier point snapping.
* Cube Builder – press the right controller trigger and drag to create a cube. This simple tool is included mostly as an example.
* Selection Mode – select and edit an object in 3D space.
* Dragging Mode – select and drag an object in 3D space. If the object is part of an assembly, it must have 6 DOF and must be constrained with GroundedJoint. Dragging works by changing the object’s placement. The assembly solver detects the constrained object’s placement change and adjusts the placement of other objects.
* Working Plane – allows you to set a working plane with the right controller ray. It is useful for Line Builder, as vertices can be snapped to the plane.
* Toggle Overlay – toggles the projection of the main window’s Qt widgets in 3D space. By default, the Tree View and Tasks View are projected. The right controller ray emulates mouse pointing, including left mouse click and double-click. Right mouse click and dragging are not implemented yet.

### Selection mode (EXPERIMENTAL)
If Selection Mode is enabled, pointing the right controller ray at an object and pressing the trigger displays an edit menu near the right controller. For example:

1. Point the ray and press the trigger on a face to select it. If a body does not exist, it will be created.
2. Select Pad; the button will turn green.
3. Point the ray and press the trigger again, then start dragging. The face will continuously extrude until you release the trigger.

## Tips and tricks:

SteamVR:

SteamVR checks the proximity sensor in the HMD, so the user must wear the HMD fully to enable rendering. Only if the head is detected the runtime will return XR_SESSION_STATE_FOCUSED required for rendering. The sensor is located in the middle of the HMD, between (slightly above) the lenses in most HMDs.

Linux specific:

Monado with libsurvive works well, including two Lighthouses setup.
In cause of issues with libsurvive tracking, Monado can use SteamVR tracking:

`STEAMVR_LH_ENABLE=true monado-service`

## Tracked third-person camera

The `Toggle third-person camera` button replaces the VR HMD mirror with a view based on an additional tracker location. A tracker's role has to be set as `CAMERA` in the OpenXR options. The relative camera position to the tracker can be adjusted in the Addon preferences. Such tracked camera was used to record the demo video shown at the beginning of the README.

[xrprefs]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/xr-prefs.png "View of preferences tab"

## OpenXR version

While all required features are available in OpenXR 1.0, some newer controllers might require a newer version of the API. The `Use the highest OpenXR version available` option forces the addon to request the runtime for the newest version supported by `pyopenxr`. If such a version is not available, the addon will fall back to 1.0.x.

## License

Check [LICENSE](LICENSE) for details.
