### Description
The program displays a group of 3D space ships that can move through the map, along with their shadows on the ground. The program also displays 5 types of randomly positioned objects and obstacles of various shapes, sizes and colors. Some of these objects are rotating.

The 3D model used by the ships, as well as it's texture, was created by me using Blender. The model of the obstacles was created as a gpu shape based on their vertices.
 
Every object, along with it's transformations, is put on a scene graph tree, to be then displayed on screen using OpenGL.

It's worth noting that obstacles don't collide with the ships, they're just visual representations.

### New to this version
You can now record different positions of the ships and then make them reproduce the movement on their own, interpolating between all of the recorded positions.

Each time you press `R`, a new checkpoint is created. When you press `1`, the ships move along the path created by the checkpoints. If you press `V` you can toggle the visualization of the path created by the points recorded so far (if a point is recorded while visualization is on, you'll need to toggle it off and on to update the visualization with the new point).

You can also change the perspective to a third person view using C.

### Controls
- `WASD` = Move
- `Mouse Up` = Tilt the ships up
- `Mouse Down` = Tilt the ships down
- `R` = Record a checkpoint.
- `1` = Reproduce the recorded movement.
- `V` = Visualize the recorded path that the ships will follow.
- `Q` = Deactivate cursor lock on window
- `C` = Change to third person view