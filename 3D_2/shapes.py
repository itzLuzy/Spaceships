import numpy as np

# Clase para los objetos que se muevan, por ahora solo la ocupa ship
class Moveable():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.spd = 30.0
        self.aspd = 8  # Rapidez angular

        self.psi = 0.0    # Rotación con respecto a x
        self.phi =   0.0  # Rotación con respecto a y
        self.theta = 0.0  # Rotación con respecto a z

        self.d = 10.0 # Distancia de los vectores auxiliares

        self.pos = np.array([self.x, self.y, self.z])
        self.fw = self.d * np.array([ 1.0, 0.0, 0.0 ]) + self.pos  # Vector 'forward'
        self.bw = self.d * np.array([-1.0, 0.0, 0.0 ]) + self.pos  # Vector 'backwards'
        self.sd = self.d * np.array([ 0.0, 0.0, 1.0 ]) + self.pos  # Vector 'side'
        self.up = self.d * np.array([ 1.0, 0.0, 0.0 ]) + self.pos  # Vector 'up'


    def rotateY(self,dphi):
        self.phi += dphi
        self.updateForward()
    
    def rotateZ(self,dtheta):
        if np.abs(self.theta + dtheta) < np.pi/3:
            self.theta += dtheta
            self.updateForward()

    def moveTo(self,x,y,z):
        self.x, self.y, self.z = x, y, z
        self.updateForward()

   # Mueve el objeto de forma continua con la velocidad indicada
    def move(self,dt,spd_x,spd_y, spd_z):
        dx = spd_x*dt
        dy = spd_y*dt
        dz = spd_z*dt
        self.x += dx
        self.y += dy
        self.z += dz
        self.updateForward()
    
    # Mueve el objeto hacia el punto indicado con la rapidez indicada
    def moveTowards(self,dt,x,y,z):
        dx = x-self.x
        dy = y-self.y
        dz = z-self.z
        sign = np.sign(self.spd)

        if abs(dx) > 0.1 or abs(dy) > 0.1 or abs(dz) > 0.1:  # Para que no divida por 0
            delta_t = np.sqrt((np.square(dx)+np.square(dy)+np.square(dz))/(np.square(self.spd)))  # Pura cinemática xd
            spd_x = sign*dx/delta_t
            spd_y = sign*dy/delta_t
            spd_z = sign*dz/delta_t
            self.move(dt,spd_x,spd_y,spd_z)
    
    # Mueve el objeto pa delante
    def moveForward(self,dt):
        x = self.fw[0]
        y = self.fw[1]
        z = self.fw[2]
        self.moveTowards(dt,x,y,z)

    def moveBackwards(self,dt):
        x = self.bw[0]
        y = self.bw[1]
        z = self.bw[2]
        self.moveTowards(dt,x,y,z)
    
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
            
    def updateForward(self):
        self.pos = np.array([self.x, self.y, self.z])
        self.fw = np.array(
            [
                np.cos(self.theta) * np.cos(self.phi),
                np.sin(self.theta),
                -np.sin(self.phi),
            ]
        )
        self.bw = -self.fw
        self.sd = np.cross(self.fw, np.array([0.0, 1.0, 0.0]))
        self.up = np.cross(self.sd, self.fw)

        self.fw = self.d * (self.fw/np.linalg.norm(self.fw)) + self.pos
        self.bw = self.d * (self.bw/np.linalg.norm(self.bw)) + self.pos
        self.sd = self.d * (self.sd/np.linalg.norm(self.sd)) + self.pos
        self.up = self.d * (self.up/np.linalg.norm(self.up)) + self.pos


class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    def __str__(self):
        return "vertices: " + str(self.vertices) + "\n"\
            "indices: " + str(self.indices)

def createColorCube(r, g, b):

    vertices = [
    #    positions        colors
        -0.5, -0.5,  0.5, r, g, b,
         0.5, -0.5,  0.5, r, g, b,
         0.5,  0.5,  0.5, r*.9, g*.9, b*.6,
        -0.5,  0.5,  0.5, r*.9, g*.8, b*.9,

        -0.5, -0.5, -0.5, r, g, b,
         0.5, -0.5, -0.5, r, g, b,
         0.5,  0.5, -0.5, r*.9, g*.6, b*.9,
        -0.5,  0.5, -0.5, r*.9, g*.6, b*.9]

    indices = [
         0, 1, 2, 2, 3, 0,
         4, 5, 6, 6, 7, 4,
         4, 5, 1, 1, 0, 4,
         6, 7, 3, 3, 2, 6,
         5, 6, 2, 2, 1, 5,
         7, 4, 0, 0, 3, 7]

    return Shape(vertices, indices)


def createColorQuad(r1, g1, b1, r2, g2, b2):

    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  r2, g2, b2,
         0.5, -0.5, 0.0,  r1, g1, b1,
         0.5,  0.5, 0.0,  r1, g1, b1,
        -0.5,  0.5, 0.0,  r2, g2, b2,]

    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)


def createColorCircle(N, r, g, b):

    # First vertex at the center
    colorOffsetAtCenter = 0.3
    vertices = [0, 0, 0,
        r + colorOffsetAtCenter,
        g + colorOffsetAtCenter,
        b + colorOffsetAtCenter]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,
            # color
            r, g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return Shape(vertices, indices)


def createObstacle():

    vertices = [
    #    positions        colors
        -0.5, -0.5,  0.5, 1, 0, 0.7,
         0.5, -0.5,  0.5, 1, 0, 0.7,
         0.5,  0.5,  0.5, 0.5, 0, 0.7,
        -0.5,  0.5,  0.5, 0.4, 0, 0.6,

        -0.5, -0.5, -0.5, 1, 0, 0.7,
         0.5, -0.5, -0.5, 1, 0, 0.7,
         0.5,  0.5, -0.5, 0.5, 0, 0.7,
        -0.5,  0.5, -0.5, 0.5, 0, 0.7]

    indices = [
         0, 1, 2, 2, 3, 0,
         4, 5, 6, 6, 7, 4,
         4, 5, 1, 1, 0, 4,
         6, 7, 3, 3, 2, 6,
         5, 6, 2, 2, 1, 5,
         7, 4, 0, 0, 3, 7]

    return Shape(vertices, indices)


def createGreenTriangle():

    vertices = [
    #   positions        colors
        -0.5, 0.0, -0.5,  0.0, 0.7, 0.4,    #0
         0.5, 0.0, -0.5,  0.0, 0.7, 0.4,    #1
         0.0, 0.0,  0.5,  0.0, 0.8, 0.1,    #2
         
        -0.5, -0.25, -0.5,  0.0, 0.5, 0.3,  #3
         0.5, -0.25, -0.5,  0.0, 0.5, 0.3,  #4
         0.0, -0.25,  0.5,  0.0, 0.8, 0.1,] #5
 
    indices = [0, 1, 2, 
               0, 1, 3, 0, 2, 3, 1, 2, 4,
               4, 1, 3, 5, 2, 3, 4, 2, 5,
               3, 4, 5]

    return Shape(vertices, indices)