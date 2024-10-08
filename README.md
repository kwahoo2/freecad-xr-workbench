# FreeCAD XR Workbench

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.

[Forum thread](https://forum.freecad.org/viewtopic.php?t=39526)

## Prerequisites

### Software Dependencies

* FreeCAD 0.20 or later
* Python 3.11+
* an OpenXR Runtime, it can be selected manually with:

`XR_RUNTIME_JSON=json_file_placement FreeCAD_executable`

example:

`XR_RUNTIME_JSON=/usr/local/share/openxr/1/openxr_monado.json ./FreeCAD_1.0.0-conda-Linux-x86_64-py311.AppImage`

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
