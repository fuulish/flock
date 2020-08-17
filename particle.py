
from __future__ import print_function

import numpy as np
import random
import math

from constants import *

mass_of_air = 0.1

class Particle(object):
    def __init__(self, x, y, size, speed=(0.01, 0.01), density=1.):
        """Initialize a single particle"""

        self._position = np.array((x, y), dtype='float')

        self.size = size
        self.mass = density*size**2

        self.color = color(200-density*10, 200-density*10, 255)
        self._thickness = 0

        self._speed = np.array(speed, dtype='float')

        self._drag = 1.0

        self.moving = True

    def position():
        doc = "The position property."
        def fget(self):
            return self._position
        def fset(self, value):
            self._position[:] = value[:]
        def fdel(self):
            del self._position
        return locals()
    position = property(**position())

    def speed():
        doc = "The speed property."
        def fget(self):
            return self._speed
        def fset(self, value):
            if self.moving:
                self._speed[:] = value[:]
            else:
                raise RuntimeError("Cannot set a speed for a non-moving object")
        def fdel(self):
            del self._speed
        return locals()
    speed = property(**speed())

    def color():
        doc = "The color property."
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = color(value[0], value[1], value[2])
        def fdel(self):
            del self._color
        return locals()
    color = property(**color())

    def mass():
        doc = "The mass property."
        def fget(self):
            return self._mass
        def fset(self, value):
            self._mass = value
        def fdel(self):
            del self._mass
        return locals()
    mass = property(**mass())

    def size():
        doc = "The size property."
        def fget(self):
            return self._size
        def fset(self, value):
            self._size = value
        def fdel(self):
            del self._size
        return locals()
    size = property(**size())

    def move(self):
        "move particle"

        # currently gravity acts in the wrong direction, because of this line
        self._position += self._speed

    def addGravity(self, gravity):
        self._speed[1] += gravity

    def addFriction(self):
        self._speed *= self._drag

    def mouseMove(self, x, y):

        speed = (x - self.position[0],
                 y - self.position[1])

        self.position = (x, y)
        self.speed = (speed[0]*0.1, -speed[1]*0.1)

class Environment(object):
    def __init__(self, width=640, height=480):

        self.width = width
        self.height = height
        self.background_color = white

        self.mass_of_air = 0.1
        self.gravity = 0.002
        self.elasticity = 0.75

        self.mass_of_air = 0.1

        self.particles = []

        self.one_particle_functions = []
        self.one_particle_function_dict = {
        'move' : lambda p: p.move(),
        'gravity' : lambda p: p.addGravity(self.gravity),
        'bounce' : lambda p: self.bounce(p),
        'friction' : lambda p: p.addFriction()
        }

        self.many_particle_functions = []
        self.many_particle_function_dict = {
        'collide' : lambda particles: self.collide_all(),
        }

    def addFunctions(self, function_list):
        for function in function_list:
            if function in self.one_particle_function_dict:
                self.one_particle_functions.append(self.one_particle_function_dict[function])
            elif function in self.many_particle_function_dict:
                self.many_particle_functions.append(self.many_particle_function_dict[function])
            else:
                print('No such function %s' %str(function))

    def addParticles(self, n=1, **kwargs):

        for n in range(n):
            size = kwargs.get('size', random.randint(10, 20))
            x = kwargs.get('x', random.randint(size, self.width-size))
            y = kwargs.get('y', random.randint(size, self.height-size))
            density = kwargs.get('density', random.randint(1, 20))

            pool = self.__dict__[kwargs.get('pool', 'particles')]

            pool.append(Particle(x, y, size, density=density))
            particle = pool[-1]
            particle.speed = kwargs.get('speed', (random.random(), random.random()))

            #this depends on the environment, i.e., the _thickness of our air
            particle._drag = (particle.mass / (particle.mass + self.mass_of_air)) ** particle.size

    def update(self):
        for i, particle in enumerate(self.particles):
            for f in self.one_particle_functions:
                f(particle)

        for f in self.many_particle_functions:
            f(self.particles)

        #now all the multi-particle functions
            #particle.move()

        #self.bounce()
        #addGravity(self.particles, self.gravity)
        #addFriction(self.particles)
        #collide_all(self.particles)

    def bounce(self, particle):

        #for particle in self.particles:
        if particle.position[0] > self.width - particle._size:
            particle.position[0] = 2 * (self.width - particle._size) - particle.position[0]
            particle._speed[0] = -particle._speed[0] * self.elasticity

        elif particle.position[0] < particle._size:
            particle.position[0]  = 2 * particle._size - particle.position[0]
            particle._speed[0] = -particle._speed[0] * self.elasticity

        if particle.position[1] > self.height - particle._size:
            particle.position[1] = 2 * (self.height - particle._size) - particle.position[1]
            particle._speed[1] = -particle._speed[1] * self.elasticity

        elif particle.position[1] < particle._size:
            particle.position[1] = 2 * particle._size - particle.position[1]
            particle._speed[1] = -particle._speed[1] * self.elasticity

    def findParticle(self, x, y):
        for p in self.particles:
            pos = p.position
            if math.hypot(pos[0] - x, pos[1] - y) <= p._size:
                return p

        return None

    def collide_all(self):
        for p, part in enumerate(self.particles):
            colliding = detect_collision(part, self.particles[p+1:])

            if colliding:
                dx, dy = (part.position[0]-colliding.position[0],
                          part.position[1]-colliding.position[1])

                dvx, dvy = (part.speed[0]-colliding.speed[0],
                            part.speed[1]-colliding.speed[1])

                prefactor = -2. / (part.mass + colliding.mass) * (dvx * dx + dvy * dy) / (dx**2 + dy**2) #math.hypot(dx, dy)**2
                #prefactor = -2. * colliding.mass / (part.mass + colliding.mass) * \

                part.speed = (part.speed[0] + prefactor * colliding.mass * dx,
                              part.speed[1] + prefactor * colliding.mass * dy)

                colliding.speed = (colliding.speed[0] - prefactor * part.mass * dx,
                                   colliding.speed[1] - prefactor * part.mass * dy)

                # anti-stick precaution
                dist = math.hypot(dx, dy)
                dx /= dist
                dy /= dist

                overlap = part._size + colliding._size - dist

                part.position = (part.position[0] + dx * overlap / 2.,
                             part.position[1] + dy * overlap / 2.)

                colliding = (colliding.position[0] - dx * overlap / 2.,
                             colliding.position[1] - dy * overlap / 2.)

def detect_collision(me, others):

    for oth in others:
        dx = me.position[0] - oth.position[0]
        dy = me.position[1] - oth.position[1]

        dist = math.hypot(dx, dy)

        if dist <= (me._size + oth._size):
            return oth
