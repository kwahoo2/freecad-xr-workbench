# Virtual Reality

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.

![FreeCAD-XR][fcxr]

[fcxr]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/fcxr-screen.png "View of active workbench"

## Prerequisites

* Any HMD supported by OpenXR (HTC Vive, Valve Index, Oculus Rift, or a Windows Mixed Reality headset)

Note: the OpenXR runtime has to support [XR_KHR_opengl_enable](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XR_KHR_opengl_enable.html) extension.

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

## License

Check [LICENSE](LICENSE) for details.

## More info

Check the full [README](README.md).
