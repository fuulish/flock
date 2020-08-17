from particle import Particle
import numpy as np

class Rectangle(Particle):
    def __init__(self, x,y, width=1., height=1., *args, **kwargs):

        kwargs['size'] = width * height
        super(Rectangle, self).__init__(x,y, *args, **kwargs)

        self.isrectangle = True

        self.width = width
        self.height = height

class Building(Rectangle):
    def __init__(self, *args, **kwargs):
        super(Building, self).__init__(*args, **kwargs)

        self.moving = False
        self._speed = np.zeros(2)

class Plane(Rectangle):
    def __init__(self, *args, **kwargs):
        super(Plane, self).__init__(*args, **kwargs)

        self.moving = True
