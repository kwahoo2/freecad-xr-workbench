# FreeCAD XR Workbench

A Virtual Reality (OpenXR) workbench written in Python. Aims for easier installation and more flexibility than C++ XR fork.

[Forum thread](https://forum.freecad.org/viewtopic.php?t=39526)

## Prerequisites

### Software Dependencies

* FreeCAD v0.20.xxxxx
* Python 3.10+
* an OpenXR Runtime

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

* Linux `/home/username/.local/share/FreeCAD/Mod/` or `/home/username/.FreeCAD/Mod/` for LinkDaily branch
* Windows `%APPDATA%\FreeCAD\Mod\`, which is usually `C:\Users\username\Appdata\Roaming\FreeCAD\Mod\`

See also: [FreeCAD Wiki: Installing more workbenches](https://wiki.freecad.org/Installing_more_workbenches)

A new `XR` workbench will appear.

## Known issues:

Wayland/EGL support not implemented yet.

## License

Check [LICENSE](LICENSE) for details.
