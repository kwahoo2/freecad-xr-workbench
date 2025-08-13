# Running the XR Workbench on Linux and Wayland (without XWayland)

## Current state

The FreeCAD XR Workbench can work on Linux without X11, thanks to the EGL interface, but some steps have to be performed (see below).

## Prerequisites

* The OpenXR runtime has to support [XrGraphicsBindingEGLMNDX](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XrGraphicsBindingEGLMNDX.html) It is available in SteamVR and Monado. 

* recent pyopenxr - it supports EGL since version 1.1.5001

* FreeCAD compiled with EGL-ready Coin library.

FreeCAD itself doesn't rely on X11, but it uses Coin3D library that has a GLX dependency by default.

1. Uninstall Coin3D if installed.
2. Compile and install Coin3D with EGL but without GLX:

    ```
    git clone https://github.com/coin3d/coin.git
    cd coin/build
    cmake -DCOIN_BUILD_EGL=TRUE -DCOIN_BUILD_GLX=FALSE ..
    make
    sudo make install
    ```

3. Compile and install Pivy:

    ```
    git clone https://github.com/coin3d/pivy.git
    cd pivy/
    mkdir build
    cd build
    cmake .. --toolchain $VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE:STRING=Release -DX_VCPKG_APPLOCAL_DEPS_INSTALL:BOOLEAN=ON
    cmake --build .
    sudo make install
    ```

4. Compile FreeCAD.
