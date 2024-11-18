import pyglet
import numpy as np
import random

import libs.transformations as tr
import libs.scene_graph as sg

import shapes as sh
import libs.easy_shaders as es

from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from ship import Ship

from OpenGL.GL import *

WIDTH, HEIGHT = 1280, 768

ASSETS = {
    "ship_obj": getAssetPath("ship_tex.obj"),
    "ship_shadow": getAssetPath("ship_shadow.obj")
}

# Indicates the movement of the ship
MOVE = {
    "FW": False,   # Forward movement
    "BW": False,   # Backwards movement
    "CW": False,   # Clockwise rotation (y axis)
    "ACW": False,  # Anti-clockwise rotation (y axis)
}

class World:
    def __init__(self, limit_x=15, limit_y=10, limit_z=15) -> None:
        self.lx = limit_x
        self.ly = limit_y
        self.lz = limit_z
        self.timer = 0.0
        
class Camera:
    def __init__(self) -> None:
        self.at = np.array([0.0, 0.0, 0.0])
        self.eye = np.array([-500.0, 500.0, 300.0])
        self.up = np.array([0.0, 1.0, 0.0])
        self.projection = tr.ortho(-WIDTH*.017, WIDTH*.017, -HEIGHT*.017, HEIGHT*.017, 0.01, 1000)
        self.projection_name = "ortho"
    
    def follow(self, ship):
        if self.projection_name == "ortho":
            self.at[0] = ship.x
            self.at[1] = ship.y
            self.at[2] = ship.z
            self.eye[0] = -500
            self.eye[1] = 500
            self.eye[2] = 400
        elif self.projection_name == "perspective":
            self.at = ship.pos
            self.eye[0] = ship.bw[0]
            self.eye[1] = ship.bw[1] + 5
            self.eye[2] = ship.bw[2]
    
    def changeProjection(self, ship):
        if self.projection_name == "ortho":
            self.projection_name = "perspective"
            self.projection = tr.perspective(75,WIDTH/HEIGHT,0.01,1000) # POV
            ship.aspd = 4
            ship.spd = 10
        
        elif self.projection_name == "perspective":
            self.projection_name = "ortho"
            self.projection = tr.ortho(-WIDTH*.017, WIDTH*.017, -HEIGHT*.017, HEIGHT*.017, 0.01, 1000)
            ship.aspd = 8
            ship.spd = 20



## Scene graphs

# Ship fleet graph
def createFleet(ship_shape, ship_shadow, d = 1.5):
    shipL2 = sg.SceneGraphNode("shipL2")
    shipL2.childs += [ship_shape]

    shipR2 = sg.SceneGraphNode("shipR2")
    shipR2.childs += [ship_shape]

    shipL2_shadow = sg.SceneGraphNode("shipL2_shadow")
    shipL2_shadow.childs += [ship_shadow]

    shipL2_shadow_pos = sg.SceneGraphNode("shipL2_shadow_pos")
    shipL2_shadow_pos.transform = tr.translate(-d, 0.0, -d)
    shipL2_shadow_pos.childs += [shipL2_shadow]

    shipL2_pos = sg.SceneGraphNode("shipL2_pos")
    shipL2_pos.transform = tr.translate(-d, 0.0, -d)
    shipL2_pos.childs += [shipL2]

    shipR2_shadow = sg.SceneGraphNode("shipR2_shadow")
    shipR2_shadow.childs += [ship_shadow]

    shipR2_shadow_pos = sg.SceneGraphNode("shipR2_shadow_pos")
    shipR2_shadow_pos.transform = tr.translate(-d, 0.0, d)
    shipR2_shadow_pos.childs += [shipR2_shadow]

    shipR2_pos = sg.SceneGraphNode("shipR2_pos")
    shipR2_pos.transform = tr.translate(-d, 0.0, d)
    shipR2_pos.childs += [shipR2]

    shipL1 = sg.SceneGraphNode("shipL1")
    shipL1.childs += [ship_shape]

    shipR1 = sg.SceneGraphNode("shipR1")
    shipR1.childs += [ship_shape]

    shipL1_shadow = sg.SceneGraphNode("shipL1_shadow")
    shipL1_shadow.childs += [ship_shadow]

    shipL1_shadow_pos = sg.SceneGraphNode("shipL1_shadow_pos")
    shipL1_shadow_pos.transform = tr.translate(-d, 0.0, -d)
    shipL1_shadow_pos.childs += [shipL1_shadow]
    shipL1_shadow_pos.childs += [shipL2_shadow_pos]

    shipL1_pos = sg.SceneGraphNode("shipL1_pos")
    shipL1_pos.transform = tr.translate(-d, 0.0, -d)
    shipL1_pos.childs += [shipL1]
    shipL1_pos.childs += [shipL2_pos]

    shipR1_shadow = sg.SceneGraphNode("shipR1_shadow")
    shipR1_shadow.childs += [ship_shadow]

    shipR1_shadow_pos = sg.SceneGraphNode("shipR1_shadow_pos")
    shipR1_shadow_pos.transform = tr.translate(-d, 0.0, d)
    shipR1_shadow_pos.childs += [shipR1_shadow]
    shipR1_shadow_pos.childs += [shipR2_shadow_pos]

    shipR1_pos = sg.SceneGraphNode("shipR1_pos")
    shipR1_pos.transform = tr.translate(-d, 0.0, d) 
    shipR1_pos.childs += [shipR1]
    shipR1_pos.childs += [shipR2_pos]

    ship0 = sg.SceneGraphNode("ship0")
    ship0.childs += [ship_shape]

    ship0_shadow = sg.SceneGraphNode("ship0_shadow")
    ship0_shadow.childs += [ship_shadow]

    ship0_shadow_pos = sg.SceneGraphNode("ship0_shadow_pos")
    ship0_shadow_pos.transform = tr.matmul(
            [
                tr.translate(0.0, -world.ly + 0.03, 0.0),
                tr.scale(1.0, 0.0, 1.0)
            ]
        )
    ship0_shadow_pos.childs += [ship0_shadow]
    ship0_shadow_pos.childs += [shipL1_shadow_pos]
    ship0_shadow_pos.childs += [shipR1_shadow_pos]

    ship0_pos = sg.SceneGraphNode("ship0_pos")
    ship0_pos.childs += [shipL1_pos]
    ship0_pos.childs += [shipR1_pos]
    ship0_pos.childs += [ship0]
    ship0_pos.childs += [ship0_shadow_pos]

    fleet = sg.SceneGraphNode("fleet")
    fleet.childs += [ship0_pos]

    return fleet

# Main scene graph
def createSceneGraph(fleet):
    trajectory = sg.SceneGraphNode("trajectory")

    spdboosts = sg.SceneGraphNode("spdboosts")

    meteorites = sg.SceneGraphNode("meteorites")
     
    lifegems = sg.SceneGraphNode("lifegems")

    portals = sg.SceneGraphNode("portals")

    obstacles = sg.SceneGraphNode("obstacles")
    
    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul(
            [
                tr.translate(8.0, -world.ly, 0.0),
                tr.rotationX(np.pi/2),
                tr.scale(7*world.lx, 2*world.lz, 0.0)
            ]
        )
    floor.childs += [gpu_floor]

    border = sg.SceneGraphNode("border")
    border.transform = tr.matmul(
            [
                tr.translate(0.0, -world.ly+0.01, 0.0),
                tr.rotationX(np.pi/2),
                tr.scale(2*world.lx, 2*world.lz, 0.0)
            ]
        )
    border.childs += [gpu_border]
    
    root = sg.SceneGraphNode("root")
    root.childs += [obstacles]
    root.childs += [fleet]
    # root.childs += [border]
    root.childs += [floor]
    root.childs += [portals]
    root.childs += [lifegems]
    root.childs += [meteorites]
    root.childs += [spdboosts]
    root.childs += [trajectory]

    return root



## Auxiliary functions for the ships

# Transforms ships according to their position and rotation
def updateShipTransform(ship):
    node = sg.find_node(scene, "ship0_pos")
    shadow = sg.find_node(scene, "ship0_shadow_pos")
    x, y, z, phi, theta = ship.x, ship.y, ship.z, ship.phi, ship.theta
    node.transform = tr.matmul(
        [
            tr.translate(x, y, z),
            tr.rotationY(phi),
            tr.rotationZ(theta),
        ]
    )
    shadow.transform = tr.matmul(
            [
                tr.rotationZ(-theta),
                tr.translate(0.0, -(y + world.ly - 0.03), 0.0),
                tr.scale(np.cos(theta), 0.0, 1.0),
            ]
        )

# Maintaints the main ship inside the world borders
def checkBorders(ship):
    x,y,z = ship.x, ship.y, ship.z
    node = sg.find_node(scene, "ship0_pos")
    if np.abs(ship.x) > world.lx:
        ship.x = np.sign(ship.x)*world.lx
        node.transform = tr.matmul(
            [   
                tr.translate(ship.x, 0.0, 0.0),
                tr.translate(-x, 0.0, 0.0),
                node.transform
            ]
        )
    if ship.y > world.ly:
        ship.y = world.ly
        node.transform = tr.matmul(
            [   
                tr.translate(0.0, ship.y, 0.0),
                tr.translate(0.0, -y, 0.0),
                node.transform
            ]
        )
    elif ship.y < -world.ly + 0.5:
        ship.y = -world.ly + 0.5
        node.transform = tr.matmul(
            [   
                tr.translate(0.0, ship.y, 0.0),
                tr.translate(0.0, -y, 0.0),
                node.transform
            ]
        )
    if np.abs(ship.z) > world.lz - 0.25:
        ship.z = np.sign(ship.z)*(world.lz-0.25)
        node.transform = tr.matmul(
            [   
                tr.translate(0.0, 0.0, ship.z),
                tr.translate(0.0, 0.0, -z),
                node.transform
            ]
        )
    ship.updateForward()





## Functions for the curves
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

# Catmull-Rom Splines
def generateTangents(points, t0, tf):
    tangentes = []
    for i in range(len(points)):
        if i == 0:
            tangentes.append(t0)
        elif i == len(points) - 1:
            tangentes.append(tf)
        else:
            t = (points[i + 1] - points[i - 1])/2
            tangentes.append(t)
    return tangentes


def hermiteMatrix(P1, P2, T1, T2):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)

    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

    return np.matmul(G, Mh)


# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

    return curve


N = 3000
step = 0
points_covered = 0
RECORDING = True
VIEWING = False
checkpoints = []
t0 = np.array([])
tf = np.array([])
recording = []


def create_record_points():
    global recording, angles, checkpoints, t0, tf
    if len(checkpoints) >= 2:
        tangentes = generateTangents(checkpoints, t0, tf)
        i = 0
        for i in range(len(checkpoints)-1):
            hm = hermiteMatrix(checkpoints[i], checkpoints[i+1],
                                 tangentes[i],   tangentes[i+1])
            curve = evalCurve(hm, N)
            recording.append(curve)


# Window creation
window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

# Ship controls
@window.event
def on_mouse_motion(x, y, dx, dy):
    if RECORDING:
        if np.abs(dy)>10:
            dtheta = 0.003*10*dy/np.abs(dy)
        else:
            dtheta = 0.003*dy

        ship_3d.rotateZ(dtheta)
        updateShipTransform(ship_3d)


@window.event
def on_key_press(symbol, modifiers):
    global recording, step, checkpoints, points_covered, t0, tf, MOVE, RECORDING, VIEWING
    if symbol == pyglet.window.key.W and RECORDING:
        MOVE["FW"] = True

    if symbol == pyglet.window.key.S and RECORDING:
        MOVE["BW"] = True

    if symbol == pyglet.window.key.A and RECORDING:
        MOVE["ACW"] = True

    if symbol == pyglet.window.key.D and RECORDING:
        MOVE["CW"] = True
    
    if symbol == pyglet.window.key._1 and RECORDING == True:
        RECORDING = False
        step = 0
        points_covered = 0
        MOVE["FW"] = False
        MOVE["BW"] = False
        MOVE["ACW"] = False
        MOVE["CW"] = False
        if len(recording) == 0:
            create_record_points()

    # Records a checkpoint
    if symbol == pyglet.window.key.R and RECORDING == True:
        checkpoints.append(np.array([[ship_3d.x, ship_3d.y, ship_3d.z]]).T)
        coso = ship_3d.fw - ship_3d.pos
        if t0.size == 0:
            t0 = np.array([[coso[0], coso[1], coso[2]]]).T
        tf = np.array([[coso[0], coso[1], coso[2]]]).T
    
    if symbol == pyglet.window.key.V:
        if not VIEWING:
            VIEWING = True
            if len(recording) == 0:
                create_record_points()
            for road in recording:
                for k in range(0,len(road),100):
                    pos = road[k]
                    trajectory = sg.find_node(scene, "trajectory")
                    point = sg.SceneGraphNode("point" + str(len(trajectory.childs)))
                    point.transform = tr.matmul(
                        [
                            tr.translate(pos[0], pos[1], pos[2]),
                            tr.uniformScale(0.05)
                        ]
                    )
                    point.childs += [gpu_point]
                    trajectory.childs += [point]
        else:
            VIEWING = False
            trajectory = sg.find_node(scene, "trajectory")
            trajectory.childs.clear()
            if RECORDING:
                recording.clear()
    
    # Deactivates cursor lock on window
    if symbol == pyglet.window.key.Q:
        window.set_exclusive_mouse(False)
    
    if symbol == pyglet.window.key.C:
        camera.changeProjection(ship_3d)

@window.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.W and RECORDING:
        MOVE["FW"] = False

    if symbol == pyglet.window.key.S and RECORDING:
        MOVE["BW"] = False

    if symbol == pyglet.window.key.A and RECORDING:
        MOVE["ACW"] = False

    if symbol == pyglet.window.key.D and RECORDING:
        MOVE["CW"] = False



## Object generators
@window.event
def generateObstacle(dt):
    obstacles = sg.find_node(scene, "obstacles")
    obs = sg.SceneGraphNode("obstacle" + str(len(obstacles.childs)))
    obs.transform = tr.matmul(
            [
                tr.translate(world.lx*4, 0.0, random.uniform(-(world.lz-7), (world.lz-7))),
                tr.shearing(0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            random.uniform(-0.5,0.5),),
                tr.scale(5.0, world.ly+10, 5.0)
            ]
        )
    obs.childs += [gpu_obstacle]
    obstacles.childs += [obs]

@window.event
def generatePortal(dt):
    portals = sg.find_node(scene, "portals")
    portal = sg.SceneGraphNode("obstacle" + str(len(portals.childs)))
    portal.transform = tr.matmul(
            [
                tr.translate(world.lx*4, 0.0, random.uniform(-(world.lz-7), (world.lz-7))),
                tr.rotationY(np.pi/2),
                tr.scale(3.0, 6.0, 3.0)
            ]
        )
    portal.childs += [gpu_portal]
    portals.childs += [portal]

@window.event
def generateLifegem(dt):
    lifegems = sg.find_node(scene, "lifegems")
    gem = sg.SceneGraphNode("lifegem" + str(len(lifegems.childs)))
    gem.transform = tr.matmul(
            [
                tr.translate(world.lx*4, 0.0, random.uniform(-(world.lz-7), (world.lz-7))),
                tr.rotationZ(np.pi/4),
                tr.rotationX(np.pi/4)
            ]
        )
    gem.childs += [gpu_lifegem]
    lifegems.childs += [gem]

@window.event
def generateMeteorite(dt):
    meteorites = sg.find_node(scene, "meteorites")
    met = sg.SceneGraphNode("meteorite" + str(len(meteorites.childs)))
    met.transform = tr.matmul(
            [
                tr.translate(random.uniform(-(world.lx-1), (world.lx-1)),
                            random.uniform(-(world.ly-7), (world.ly-7)),
                            -4*world.lz),
                tr.rotationZ(np.pi/4),
                tr.rotationX(np.pi/4),
                tr.uniformScale(2.5)
            ]
        )
    met.childs += [gpu_meteorite]
    meteorites.childs += [met]

@window.event
def generateSpdboost(dt):
    spdboosts = sg.find_node(scene, "spdboosts")
    boost = sg.SceneGraphNode("spdboost" + str(len(spdboosts.childs)))
    boost.transform = tr.matmul(
            [
                tr.translate(world.lx*4, 0.0, random.uniform(-(world.lz-7), (world.lz-7))),
                tr.rotationY(np.pi/2),
                tr.uniformScale(2)
            ]
        )
    boost.childs += [gpu_spdboost]
    spdboosts.childs += [boost]



## Object updater
@window.event
def updateObjects(dt):
    obstacles = sg.find_node(scene, "obstacles")
    spdboosts = sg.find_node(scene, "spdboosts")
    lifegems = sg.find_node(scene, "lifegems")
    meteorites = sg.find_node(scene, "meteorites")
    portals = sg.find_node(scene, "portals")
    
    for obj in obstacles.childs:
        if obj.transform[0][3]<-world.lx*4: # If out of the scene, it's deleted
            obstacles.childs.remove(obj)
        else:
            obj.transform = tr.matmul(
                [
                    tr.translate(-20*dt, 0.0, 0.0),
                    obj.transform
                ]
            )
    for obj in spdboosts.childs:
        if obj.transform[0][3]<-world.lx*4: # If out of the scene, it's deleted
            spdboosts.childs.remove(obj)
        else:
            obj.transform = tr.matmul(
                [
                    tr.translate(-12*dt, 0.0, 0.0),
                    obj.transform
                ]
            )
    for obj in lifegems.childs:
        if obj.transform[0][3]<-world.lx*4: # If out of the scene, it's deleted
            lifegems.childs.remove(obj)
        else:
            obj.transform = tr.matmul(
                [
                    tr.translate(-7*dt, 0.0, 0.0),
                    obj.transform
                ]
            )
    for obj in meteorites.childs:
        if obj.transform[2][3]>world.lz*4: # If out of the scene, it's deleted
            meteorites.childs.remove(obj)
        else:
            obj.transform = tr.matmul(
                [
                    tr.translate(0.0, 0.0, 15*dt),
                    tr.translate(obj.transform[0][3],
                                 obj.transform[1][3],
                                 obj.transform[2][3],),
                    tr.rotationX(8*dt),
                    tr.translate(-obj.transform[0][3],
                                 -obj.transform[1][3],
                                 -obj.transform[2][3],),
                    obj.transform
                ]
            )
    for obj in portals.childs:
        if obj.transform[0][3]<-world.lx*4: # If out of the scene, it's deleted
            portals.childs.remove(obj)
        else:
            obj.transform = tr.matmul(
                [
                    tr.translate(-10*dt, 0.0, 0.0),
                    obj.transform
                ]
            )


def getAngles(vector1, vector2):
        v = vector2 - vector1
        d = np.linalg.norm(v)
        theta = np.arcsin(v[1]/d)
        cos = v[0]/d
        sin = -v[2]/d

        if cos >= 0 and sin >= 0:
            phi = np.arccos(cos)
        elif cos <= 0 and sin >= 0:
            phi = np.arccos(cos)
        elif cos <= 0 and sin <= 0:
            phi = np.arccos(-cos) + np.pi
        elif cos >= 0 and sin <= 0:
            phi = np.arcsin(cos) + 3*np.pi/2
        
        return theta, phi


## Ship updater
@window.event
def updateFleet(dt):
    global RECORDING, VIEWING, points_covered, recording, checkpoints, step, t0, tf
    dphi = ship_3d.aspd*dt

    if not RECORDING:
        if step >= N-1:
            points_covered += 1
            step = 0
        step += 1

        if points_covered > len(recording) - 1:
            step = 0
            points_covered = 0
            RECORDING = True
            checkpoints = []
            t0 = np.array([])
            tf = np.array([])
            recording = []
            VIEWING = False
            trajectory = sg.find_node(scene, "trajectory")
            trajectory.childs.clear()

        elif step >= N - 2 and points_covered + 1 < len(recording):
            forward = np.array([recording[points_covered + 1][0, 0], recording[points_covered + 1][0, 1], recording[points_covered + 1][0, 2]])
            theta, phi = getAngles(ship_3d.pos, forward)
            ship_3d.theta, ship_3d.phi = theta, phi
            ship_3d.moveTo(recording[points_covered + 1][step, 0], recording[points_covered + 1][step, 1], recording[points_covered + 1][step, 2])

        elif step < N - 1:
            forward = np.array([recording[points_covered][step + 1, 0], recording[points_covered][step + 1, 1], recording[points_covered][step + 1, 2]])
            theta, phi = getAngles(ship_3d.pos, forward)
            ship_3d.phi = phi
            ship_3d.theta = theta
            ship_3d.moveTo(recording[points_covered][step, 0], recording[points_covered][step, 1], recording[points_covered][step, 2])

    if MOVE["FW"]:
        ship_3d.moveForward(dt)
    
    if MOVE["BW"]:
        ship_3d.moveBackwards(dt)
    
    if MOVE["CW"]:
        ship_3d.rotateY(-dphi)
    
    if MOVE["ACW"]:
        ship_3d.rotateY(dphi)
    
    updateShipTransform(ship_3d)
    # checkBorders(ship_3d)
    world.timer += dt


# Objects display
@window.event
def on_draw():
    window.clear()
    # glClearColor(np.abs(np.sin(world.timer+2))/1.3, 
    #              np.abs(np.sin(world.timer-2))/1.3, 
    #              np.abs(np.sin(world.timer))/1.3,
    #              1.0
    #              )
    glClearColor(0.02, 0.0, 0.12, 1)
    camera.follow(ship_3d)
    view = tr.lookAt(camera.eye, camera.at, camera.up)

    ship_3d.setup_program(view, camera.projection)
    ship_shadow.setup_program(view, camera.projection)

    glUseProgram(simple_pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(simple_pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    glUniformMatrix4fv(glGetUniformLocation(simple_pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(simple_pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    
    sg.draw_scenegraph_node(scene,simple_pipeline,"model")



if __name__ == '__main__':
    window.set_exclusive_mouse(True)

    display = pyglet.canvas.Display()
    screen_width, screen_height = display.get_default_screen().width , display.get_default_screen().height
    window.set_location((screen_width-WIDTH)//2, (screen_height-HEIGHT)//2)

    simple_pipeline = es.SimpleModelViewProjectionShaderProgram()

    point_shape = sh.createColorCube(1,1,1)
    gpu_point = createGPUShape(simple_pipeline, point_shape)
    
    floor_shape = sh.createColorQuad(0.0, 0.8, 0.7, 0.0, 0.3, 0.6)
    gpu_floor = createGPUShape(simple_pipeline,floor_shape)

    border_shape = sh.createColorQuad(0.0, 0.8, 0.6, 0.0, 0.5, 0.6)
    gpu_border = createGPUShape(simple_pipeline,border_shape)
    
    obstacle_shape = sh.createObstacle() #1
    gpu_obstacle = createGPUShape(simple_pipeline,obstacle_shape)
    
    portal_shape = sh.createColorCircle(30,0.0,0.4,0.8) #2
    gpu_portal = createGPUShape(simple_pipeline,portal_shape)
    
    lifegem_shape = sh.createColorCube(0.9,0.0,0.4) #3
    gpu_lifegem = createGPUShape(simple_pipeline,lifegem_shape)

    meteorite_shape = sh.createColorCube(0.9,0.3,0.1) #4
    gpu_meteorite = createGPUShape(simple_pipeline,meteorite_shape)

    spdboost_shape = sh.createGreenTriangle() #5
    gpu_spdboost = createGPUShape(simple_pipeline, spdboost_shape)

    ship_3d = Ship(ASSETS["ship_obj"])
    ship_shadow = Ship(ASSETS["ship_shadow"])

    world = World(limit_z=30)
    camera = Camera()

    fleet = createFleet(ship_3d, ship_shadow)
    scene = createSceneGraph(fleet)

    pyglet.clock.schedule_interval(generateObstacle, 12)
    pyglet.clock.schedule_interval(generateLifegem, 16)
    pyglet.clock.schedule_interval(generateMeteorite, 13)
    pyglet.clock.schedule_interval(generatePortal, 17)
    pyglet.clock.schedule_interval(generateSpdboost, 15)
    pyglet.clock.schedule(updateFleet)
    pyglet.clock.schedule(updateObjects)
    pyglet.app.run()