## General Description
This is a university project for a 'Computer Graphics' course, in which the goal is to display representations of spaceships, both on 2D and 3D, making use of pyglet and OpenGL. Every object in the scene must be represented in a scene graph tree that contains their shape and transformations.

## Description of each program

### 2D
The program displays a group of 2D space ships and a bunch of randomly generated stars going from top to bottom of the screen, giving the illusion of movement on the ships.

Every object displayed on screen is created using pyglet shapes and batches.

You can also move the main ship with the keyboard arrows and the rest of them will follow with a certain delay. The screen is resizable.

![Spaceships2D](screenshots\sc_2D.png)

### 3D_1
The program displays a group of 3D space ships that can move through the map, along with their shadows on the ground. The program also displays 5 types of randomly positioned objects and obstacles of various shapes, sizes and colors. Some of these objects are rotating.

The 3D model used by the ships, as well as it's texture, was created by me using Blender. The model of the obstacles was created as a gpu shape based on their vertices.
 
Every object, along with it's transformations, is put on a scene graph tree, to be then displayed on screen using OpenGL.

It's worth noting that obstacles don't collide with the ships, they're just visual representations.

![Spaceships3D1](screenshots\sc_3D_1.png)

### 3D_2
Almost the same as 3D_1, but you can now record different positions of the ships and then make them reproduce the movement on their own, interpolating between all of the recorded positions.

Each time you press `R`, a new checkpoint is created. When you press `1`, the ships move along the path created by the checkpoints. If you press `V` you can toggle the visualization of the path created by the points recorded so far (if a point is recorded while visualization is on, you'll need to toggle it off and on to update the visualization with the new point).

You can also change the perspective to a third person view using C.

![Spaceships3D2](screenshots\sc_3D_2.png)

## Modules used
The modules used in the project are: OpenGL, pyglet, numpy, random, trimesh, PIL.

## Libraries
All the libraries used on this project (found on the `libs` folders) were provided by the professor of this course ([Eduardo Graells-Garrido](https://github.com/zorzalerrante)).