from pyglet.window import Window, key
from pyglet.app import  run
from pyglet.graphics import Batch
from pyglet import shapes, clock
from random import randint
from math import sqrt, cos
from OpenGL.GL import *



WIDTH = 1280
HEIGHT = 768
WINDOW_TITLE =  "Navecitas uwu"
FULL_SCREEN = False
window = Window(WIDTH, HEIGHT, WINDOW_TITLE, resizable=True)
window.set_fullscreen(FULL_SCREEN)
glClearColor(0.03, 0.0, 0.07, 0.0)



class Ship(Batch):
    def __init__(self,x,y,scale=3/5):
        super().__init__()
        self._x = x
        self._y = y
        self._scale = s = scale

        self._fire_l = shapes.Triangle(x, y-(s*18), x-(s*9), y-(s*18), x-(s*20), y-(s*36), color=(76, 124, 242, 255), batch=self)
        self._fire_r = shapes.Triangle(x, y-(s*18), x+(s*9), y-(s*18), x+(s*20), y-(s*36), color=(76, 124, 242, 255), batch=self)
        self._fire_c = shapes.Triangle(x, y-(s*64), x-(s*9), y-(s*18), x+(s*9), y-(s*18), color=(0, 255, 255, 220), batch=self)

        self._prop_l = shapes.Rectangle(x-(s*11), y-(s*18), (s*11), (s*32), color=(114, 114, 114, 255), batch=self)
        self._prop_r = shapes.Rectangle(x, y-(s*18), (s*11), (s*32), color=(92, 92, 92, 255), batch=self)

        self._core_l = shapes.Triangle(x, y, x-(s*64), y-(s*32), x, y+(s*96), color=(240, 140, 70, 255), batch=self)
        self._core_r = shapes.Triangle(x, y, x+(s*64), y-(s*32), x, y+(s*96), color=(235, 105, 60, 255), batch=self)

        self._wing_l = shapes.Triangle(x-(s*24), y+(s*88), x-(s*24), y-(s*24), x-(s*46), y+(s*18), color=(160, 10, 225, 255), batch=self)
        self._wing_r = shapes.Triangle(x+(s*24), y+(s*88), x+(s*24), y-(s*24), x+(s*46), y+(s*18), color=(140, 10, 210, 255), batch=self)

        self._list = [self._fire_l,self._fire_r,self._fire_c,self._prop_l,self._prop_r,self._core_l,self._core_r,self._wing_l,self._wing_r]
        self.time = 0.0

    # Continuously moves the ship with the given velocity
    def move(self,dt,speed_x,speed_y):
        dx =  (((WIDTH+HEIGHT)/2048)*100*speed_x*dt)
        dy = (((WIDTH+HEIGHT)/2048)*100*speed_y*dt)
        self._x += dx
        self._y += dy
        for part in self._list[3:]:
            part.x += dx
            part.y += dy

    # Instantly moves the ship to the given position
    def moveTo(self,x,y):
        dx = x-self._x
        dy = y-self._y
        for part in self._list[3:]:
            part.x += dx
            part.y += dy
        self._x = x
        self._y = y

    # Moves the ship to the given position with the given speed
    def moveTowards(self,dt,x,y,speed):
        delta_x = x-self._x
        delta_y = y-self._y
        if abs(delta_x) > 0.1 or abs(delta_y) > 0.1:  # Para que no divida por 0
            delta_t = sqrt((delta_x**2+delta_y**2)/(speed**2))  # Pura cinemática xd
            speed_x = delta_x/delta_t
            speed_y = delta_y/delta_t
            self.move(dt,speed_x,speed_y)

    # Rescales the ship
    def rescale(self,scale):
        self._scale = s = (scale*3/5)
        x = self._x
        y = self._y

        (self._fire_l.x, self._fire_l.x2, self._fire_l.x3) = (x, x-(s*9), x-(s*20))
        (self._fire_l.y, self._fire_l.y2, self._fire_l.y3) = (y-(s*18), y-(s*18), y-(s*36))
        (self._fire_r.x, self._fire_r.x2, self._fire_r.x3) = (x, x+(s*9), x+(s*20))
        (self._fire_r.y, self._fire_r.y2, self._fire_r.y3) = (y-(s*18), y-(s*18), y-(s*36))
        (self._fire_c.x, self._fire_c.x2, self._fire_c.x3) = (x, x-(s*9), x+(s*9))
        (self._fire_c.y, self._fire_c.y2, self._fire_c.y3) = (y-(s*64), y-(s*18), y-(s*18))

        (self._prop_l.x, self._prop_l.y) = (x-(s*11), y-(s*18))
        (self._prop_l.width, self._prop_l.height) = ((s*11), (s*32))
        (self._prop_r.x, self._prop_r.y) = (x, y-(s*18))
        (self._prop_r.width, self._prop_r.height) = ((s*11), (s*32))

        (self._core_l.x, self._core_l.x2, self._core_l.x3) = (x, x-(s*64), x)
        (self._core_l.y, self._core_l.y2, self._core_l.y3) = (y, y-(s*32), y+(s*96))
        (self._core_r.x, self._core_r.x2, self._core_r.x3) = (x, x+(s*64), x)
        (self._core_r.y, self._core_r.y2, self._core_r.y3) = (y, y-(s*32), y+(s*96))

        (self._wing_l.x, self._wing_l.x2, self._wing_l.x3) = (x-(s*24), x-(s*24), x-(s*46))
        (self._wing_l.y, self._wing_l.y2, self._wing_l.y3) = (y+(s*88), y-(s*24), y+(s*18))
        (self._wing_r.x, self._wing_r.x2, self._wing_r.x3) = (x+(s*24), x+(s*24), x+(s*46))
        (self._wing_r.y, self._wing_r.y2, self._wing_r.y3) = (y+(s*88), y-(s*24), y+(s*18))

    # Fire effect fot the ship's propeller
    def fireEffect(self):
        s = self._scale
        x = self._x
        y = self._y
        t = self.time

        (self._fire_l.x, self._fire_l.x2, self._fire_l.x3) = (x, x-(s*9), x-s*(15+3*cos(3*t)))
        (self._fire_l.y, self._fire_l.y2, self._fire_l.y3) = (y-(s*18), y-(s*18), y-(s*36))
        (self._fire_r.x, self._fire_r.x2, self._fire_r.x3) = (x, x+(s*9), x+s*(15+3*cos(3*t)))
        (self._fire_r.y, self._fire_r.y2, self._fire_r.y3) = (y-(s*18), y-(s*18), y-(s*36))
        (self._fire_c.x, self._fire_c.x2, self._fire_c.x3) = (x, x-(s*9), x+(s*9))
        (self._fire_c.y, self._fire_c.y2, self._fire_c.y3) = (y-s*(64+10*cos(2*t + 10)), y-(s*18), y-(s*18))


class Star(shapes.Star):
    def __init__(self, x, y, outer_radius=0, inner_radius=0, num_spikes=5, scale=1, rotation=randint(0,180), color=(255,255,255,255), batch=None, group=None):
        super().__init__(x, y, outer_radius, inner_radius, num_spikes, rotation, color, batch, group)
        self.scale = s = scale
        self.outer_radius = s*8
        self.inner_radius = s*4
    
    # Continuously moves the star with the given velocity
    def move(self,dt,speed_x,speed_y):
        dx =  (((WIDTH+HEIGHT)/2048)*100*speed_x*dt)
        dy = (((WIDTH+HEIGHT)/2048)*100*speed_y*dt)
        self.x += dx
        self.y += dy
    
    # Rescale the star
    def rescale(self,s):
        self.outer_radius = s*8
        self.inner_radius = s*4
        self.scale = s


# The main ship, stars on the center of the screen
ship0 = Ship(WIDTH*0.5, HEIGHT*0.5)

# Secondary ships
ship1 = Ship(ship0._x - (WIDTH/20)*3, ship0._y - HEIGHT/12)
ship2 = Ship(ship0._x + (WIDTH/20)*3, ship0._y - HEIGHT/12)
ship3 = Ship(ship0._x - (WIDTH/10)*3, ship0._y - HEIGHT/4)
ship4 = Ship(ship0._x + (WIDTH/10)*3, ship0._y - HEIGHT/4)

shiplist = [ship0,ship1,ship2,ship3,ship4]  # List that contains the ships
starlist = []                               # List that contains the stars

# Global variables to indicate wether the ship is moving or noto
MOVEX_R = False
MOVEX_L = False
MOVEY_U = False
MOVEY_D = False



@window.event
def update(dt):
    global WIDTH, HEIGHT, MOVEX_R, MOVEX_L, MOVEY_U, MOVEY_D
    
    for ship in shiplist:
        ship.time += dt   # Updates the internal time of the ships
        ship.fireEffect()

    for star in starlist:
        star.move(dt,0,-12) # Move the stars
        if star.y < 0:
            starlist.remove(star) # If a star is out of bounds, it's removed from the list

    # Main ship's movement
    spd = 5
    if MOVEX_R:
        ship0.move(dt,spd,0)
    if MOVEX_L:
        ship0.move(dt,-spd,0)
    if MOVEY_U:
        ship0.move(dt,0,spd)
    if MOVEY_D:
        ship0.move(dt,0,-spd)

    # Secondary ship's movement. They follow the main ship with a bit of delay (it looks better lol)
    ship1.moveTowards(dt, ship0._x - (WIDTH/20)*3, ship0._y - HEIGHT/12, spd-1)
    ship2.moveTowards(dt, ship0._x + (WIDTH/20)*3, ship0._y - HEIGHT/12, spd-1)
    ship3.moveTowards(dt, ship0._x - (WIDTH/10)*3, ship0._y - HEIGHT/4, spd-2)
    ship4.moveTowards(dt, ship0._x + (WIDTH/10)*3, ship0._y - HEIGHT/4, spd-2)

# The window is rescalable
@window.event
def on_resize(width,height):
    global WIDTH,HEIGHT
    # Reposition and rescale ships
    for ship in shiplist:
        ship.moveTo(width*ship._x/WIDTH, height*ship._y/HEIGHT)
        ship.rescale((width+height)/2048)

    # Rescale stars
    for star in starlist:
        star.rescale((width+height)/2048)
    
    (WIDTH,HEIGHT) = (width,height)


# Keys for movement
@window.event
def on_key_press(symbol, modifiers):
    global MOVEX_R, MOVEX_L, MOVEY_U, MOVEY_D
    if symbol == key.UP:
        MOVEY_U = True
    elif symbol == key.DOWN:
        MOVEY_D = True

    if symbol == key.RIGHT:
        MOVEX_R = True
    elif symbol == key.LEFT:
        MOVEX_L = True

@window.event
def on_key_release(symbol, modifiers):
    global MOVEX_R, MOVEX_L, MOVEY_U, MOVEY_D
    if symbol == key.UP:
        MOVEY_U = False
    elif symbol == key.DOWN:
        MOVEY_D = False

    if symbol == key.RIGHT:
        MOVEX_R = False
    elif symbol == key.LEFT:
        MOVEX_L = False

# Star generation
@window.event
def generate_stars(dt):
    global WIDTH, HEIGHT
    starlist.append(Star(randint(10,WIDTH-10),HEIGHT+232,scale=(WIDTH+HEIGHT)/2048)) # random x position

# Ships and stars are displayed on screen :)
@window.event
def on_draw():
    window.clear()
    for star in starlist:
        star.draw()
    for ship in shiplist:
        ship.draw()


clock.schedule(update)
clock.schedule_interval(generate_stars,0.03) # Stars are generated every 0.03 seconds
run()