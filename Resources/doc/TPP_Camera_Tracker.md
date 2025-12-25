# Setting up a tracker for tracked third-person camera

The `Toggle third-person camera` button replaces the VR HMD mirror view with a view based on an additional tracker location. This is useful for syncing rendered view with real world camera view and blending both views, eg. using OBS Studio and green screen (chroma key).

## Prerequisites

* A SteamVR tracker: a Vive Tracker or a custom one exposed by the `XR_HTCX_vive_tracker_interaction` extension.

## Setting tracker role in SteamVR

Open SteamVR preferences, navigate to the `Controllers` tab and open the `MANAGE TRACKERS` window. Then assign `CAMERA` role to your tracker.

![SteamVR][steamvr]

[steamvr]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/steamvr_roles.png "SteamVR tracker roles preferences"

## Setting tracker role in Monado

Support for trackers is exposed in [this Monado fork.](https://gitlab.freedesktop.org/BabbleBones/monado/-/commits/vive_tracker3/)

Building steps:

```
git clone https://gitlab.freedesktop.org/BabbleBones/monado.git
cd monado
git checkout vive_tracker3
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install
```

Then you can run the configuration utility:

`monado-gui`

Open the `Tracker Roles` window, and set the tracker role to `/user/vive_tracker_htcx/role/camera`

![Monado][monado]

[monado]: https://raw.githubusercontent.com/kwahoo2/freecad-xr-workbench/main/.github/images/monado_roles.png "Monado tracker roles preferences"

