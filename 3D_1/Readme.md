### Description
The program displays a group of 3D space ships that can move through the map, along with their shadows on the ground. The program also displays 5 types of randomly positioned objects and obstacles of various shapes, sizes and colors. Some of these objects are rotating.

The 3D model used by the ships, as well as it's texture, was created by me using Blender. The model of the obstacles was created as a gpu shape based on their vertices.
 
Every object, along with it's transformations, is put on a scene graph tree, to be then displayed on screen using OpenGL.

It's worth noting that obstacles don't collide with the ships, they're just visual representations.

### Controls
- `WASD` = Move
- `Mouse Up` = Tilt the ships up
- `Mouse Down` = Tilt the ships down
- `R` = Reset position and rotation of the ships
- `P` = Alternate between proyection types (othographic & POV)
- `Q` = Deactivate cursor lock on window