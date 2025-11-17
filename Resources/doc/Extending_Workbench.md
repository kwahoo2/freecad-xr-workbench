# Extending the XR Workbench

## Philosophy

My original implementation of Virtual Reality viewer for FreeCAD [has been written in C++](https://github.com/kwahoo2/FreeCAD/releases/tag/0.20_preXR), as an integral part of the program source code. Unfortunately this creates two issues:

* requires a separate fork or has to be merged with mainline FreeCAD,

* any change requires recompilation, making experimenting with VR much more tedious.

I decided to port the code to Python and distribute it as easy to install addon. The impact on performance is reasonable since the most of heavy lifting is done by compiled parts of FreeCAD, Coin3D and an OpenXR runtime. 

## Examples

As examples, there are two movement types implemented, add two modelling functions. Additionally, there is a minimal menu system with two widget types.

### Movement

The workbench supports "Free" and "Arch" movement types, where the first one is aimed for free translation and rotation of smaller parts, and the second one can be used to tour buildings and large areas.

The movement is always a combination of a real world movement (movement of the headset) and an artificial movement created with a controller input. Real world movement controls the camera. The controller input changes the location of the scene relative to the camera. That location is stored in `self.world_transform` SoTransform node (in the [commonXR.py](../commonXR.py)). That node can be modified in the `update_xr_movement()` where:

```
        self.world_transform.combineLeft(self.mov_xr.calculate_transformation(
            self.hmdpos, self.hmdrot,
            self.xr_con[self.primary_con],
            self.xr_con[self.secondary_con],
            final_mov_speed, final_rot_speed))
```

is called.

Function `calculate_transformation()` (a part of [movementXR.py](../movementXR.py)) checks current state of controllers (eg.: "is there a stick tilt?"), HMD and value of the `movement_type` string ("FREE" or "ARCH") and calculates the required transformation value. 

Independently from stick-driven movement, there is a teleport implementation (`check_teleport_jump()`). It creates a ray (when a controller trigger is pressed), then checks where is an intersection of the ray with an scene object. After the trigger release the user "will teleport" to location of that point.

### Modeling functions

As example there are two modeling functions implemented: one drawing straight lines, other creating cubes. Active function is selected with an enum:

```
class InteractMode(Enum):
    TELEPORT = 1
    LINE_BUILDER = 2
    CUBE_BUILDER = 3
```

and called in:

```
    def update_xr_movement(self):
...

        if self.interact_mode == InteractMode.TELEPORT:
            self.check_teleport_jump()
        elif self.interact_mode == InteractMode.LINE_BUILDER:
            self.interact_line_builder()
        elif self.interact_mode == InteractMode.CUBE_BUILDER:
            self.interact_cube_builder()
```

For example the `interact_cube_builder()` checks a controller trigger state:

* if pressed, creates a cube, using the controller location as the base,

* resizes the cube, using the controller movement as input, as long as the trigger stays pressed.

### Menu

The workbench can show a menu near to the left (primary) controller. The menu node is decoupled from the controller node, and its location has to be updated explicitly with `self.con_menu.update_location(pos, rot)`. An user presses the trigger, menu is shown near to controller, but does not move with it. The user can select the menu widget with a ray - note: the selection is done on the trigger release to avoid unintended activation. 

In the similar way, you can create other menus, and place it in different places. The menu is implemented in [menuCoin.py](../menuCoin.py). There are two widget types: button and slider, buttons can be grouped in radio groups.

