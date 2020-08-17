
from __future__ import print_function

import numpy as np

from constants import *
from particle import Particle, Environment

from cached_property import cached_property

from collections import defaultdict, namedtuple

from entity import Building, Plane

# building = namedtuple('building', 'x,y,width,height')

# TODO: number_of_birds as property and not keeping track of it every single step

class Bird(Particle):
    def __init__(self, *args, **kwargs):
        #super.__init__(**kwargs)
        super(Bird, self).__init__(*args, **kwargs)

class Flock(Environment):
    def __init__(self, *args, **kwargs):
        #super.__init__(**kwargs)
        super(Flock, self).__init__(*args, **kwargs)

        self.many_particle_function_dict.update({
                'cohere' : lambda particles: self.addCohesion(),
                'chill' : lambda particles: self.addChill(),
                'align' : lambda particles: self.addAlignment(),
            })

        self.one_particle_function_dict.update({
                'randomize' : lambda particles: self.addRandom(),
            })

        self.number_of_birds = 0
        self.birds = self.particles
        self.sitting = []
        self.speed_limit = 10.

        # might need to balance a couple of terms here
        self.adhesive = 0.01
        self.alignive = 0.01
        self.biassive = 0.05
        self.randosive = 0.001
        self.repulsion_gel = 1.
        #self.mass_of_air = 0.1

        self.death_zone = 0.10 * self.width
        self.death_zone_speed = 0.

        self.advance = 0.
        self.speed = 0.

        self.limbo = defaultdict(lambda : 0)

        self.dead_birds = []
        self.graveyard = []

        self.houses = []
        self.planes = []

        self.env_speed = 1.0
        self.bird_resilience = 10

        self.take_off_dist = 0.25 * self.height
        self.take_off_dist_sqr = self.take_off_dist**2

        self.bird_speed_increase = 0.25

        self.backup_color = None
        self.default_bird_size = 5

        self.start_com = None
        self.distance_travelled = 0.

        self.allow_new_entities = True

        self.paused = False

        # self.max_building_height = 0.75 * self.height
        # self.building_increase_factor = 1.0

    @cached_property
    def com(self):
        return self.calculate_center_of_mass()

    @cached_property
    def avel(self):
        return self.calculate_average_velocity()

    def update(self):

        # this is annoying, find a better way
        if 'com' in self.__dict__:
            del self.__dict__['com']

        if 'avel' in self.__dict__:
            del self.__dict__['avel']

        # need to reset positions according to advance of screen, otherwise bounce will fail in super

        if self.start_com is None:
            self.start_com = self.com

        self.reset_advance()

        super(Flock, self).update()

        dst = self.com - self.start_com
        self.distance_travelled = np.sign(dst[0]) * np.linalg.norm(dst)

        self.limit_bird_speed()
        self.limit_death_zone()

        alive = self.update_bird_status()
        self.update_dead_birds()

        self.update_entities()
        self.update_moving_entities()

        self.update_advance()
        # self.update_scene()

        # update visible or something like that...

        #print(self.advance)

        # TODO: remove buildings that have gone left out of the screen

        return alive

    def update_entities(self):

        addBuilding = False
        addPlane = False

        if self.speed > 0.1 and self.allow_new_entities:
            if len(self.houses) != 0:
                if self.houses[-1].position[0] + self.houses[-1].width < self.width:
                    addBuilding = True
            else:
                addBuilding = True

            if len(self.planes) != 0:
                if self.planes[-1].position[0] + self.planes[-1].width < self.width:
                    addPlane = True
            else:
                addPlane = True

            if addBuilding:
                if np.random.rand() > 0.5:
                    addBuilding = False

            if addPlane:
                if np.random.rand() > 0.5:
                    addPlane = False

            if addPlane:
                self.addPlane()

            if addBuilding:
                self.addBuilding()
                # something like that for adding new birds, new birds should also not immediately follow the flock
                if self.houses[-1].height < 0.35 * self.height and \
                   self.houses[-1].width > 10 and \
                   self.houses[-1].height > 0.10 * self.height:
                    self.addBirds(n=1, size=self.default_bird_size, density=10.,
                        x=self.houses[-1].position[0] + self.houses[-1].width*0.5,
                            y=self.houses[-1].position[1]-self.default_bird_size-1,
                            speed=(0., 0.,), pool='sitting')
                            # do something about their color?

    def limit_death_zone(self):
        self.death_zone = max([0, self.death_zone])

    def update_advance(self):
        if self.com[0] > 2. * self.width / 3:
            self.speed = 2. * self.env_speed
            self.death_zone_speed = self.env_speed
        elif self.com[0] > self.width / 2:
            self.speed = self.env_speed
            self.death_zone_speed = self.env_speed
        elif self.com[0] < self.width / 2:
            self.speed = 0.0
            self.death_zone_speed = 0.5 * self.env_speed

        self.death_zone += self.death_zone_speed
        self.advance += self.speed

    def reset_advance(self):
        for bird in self.birds:
            bird.position[0] -= self.advance

        for sitting in self.sitting:
            sitting.position[0] -= self.advance

        # TODO: better handling of self.advance and speed
        # TODO: also, use general function that moves Particles and can be used
        #       for every particles -> this necessitates the use of addParticles
        #       also for buildings and planes (easy 'nough)
        # use a different data structure
        for house in self.houses:
            house.position[0] -= self.advance

            if (house.position[0] + house.width < 0):
                self.houses.remove(house)

        for plane in self.planes:
            plane.position[0] -= self.advance

            if (plane.position[0] + plane.width < 0):
                self.planes.remove(plane)

        # one could also shift this routine to the display specific stuff
        for bird in self.dead_birds:
            if not (bird.position[0]-bird.size) <= 0:
                bird.position[0] -= self.advance
            else:
                if bird in self.dead_birds:
                    self.dead_birds.remove(bird)
                if bird in self.graveyard:
                    self.graveyard.remove(bird)

                # TODO: make sure that this is handled
                self.number_of_birds -= 1

        self.death_zone -= self.advance
        self.start_com[0] -= self.advance
        self.advance = 0.


    def update_bird_status(self):
        for b, bird in enumerate(self.birds):
            if bird.position[0] < self.death_zone:
                self.limbo[b] += 1

            if self.limbo[b] and bird.position[0] > self.death_zone:
                self.limbo[b] -= 1

            # magic value alert
            if self.limbo[b] >= self.bird_resilience:
                self.birds.remove(bird)
                self.dead_birds.append(bird)
                self.dead_birds[-1].speed *= 0.50

                # self.number_of_birds -= 1
                # print('NUM: ', self.number_of_birds, len(self.dead_birds))

                del self.limbo[b]

        for sitting in self.sitting:
            # for now just check if it's close to the center of mass of the flock
            # checking for each particle appears to costly
            dstsqr = ((sitting.position - self.com)**2).sum()

            if dstsqr < self.take_off_dist_sqr:
                # print('new birdie', dstsqr, self.take_off_dist_sqr)
                self.birds.append(sitting)
                self.sitting.remove(sitting)

                self.number_of_birds += 1

        self.birds_colliding()

        # assert self.number_of_birds == len(self.birds)
        # assert self.number_of_birds >= 0
        return self.number_of_birds - len(self.dead_birds)

    def update_moving_entities(self):

        for plane in self.planes:
            plane.position += plane.speed

    def update_dead_birds(self):

        for bird in self.dead_birds:
            if bird not in self.graveyard:
                bird.move()
                bird.addGravity(self.gravity)
                #self.bounce(bird)

                if bird.position[1] >= self.height - bird.size*1.2:
                    self.graveyard.append(bird)

    def addBirds(self, *args, **kwargs):
        if kwargs.get('pool', 'particles') == 'particles':
            self.number_of_birds += kwargs.get('n', 0)

        if not 'size' in kwargs:
            kwargs['size'] = self.default_bird_size

        self.addParticles(*args, **kwargs)

        if self.backup_color is None:
            self.backup_color = self.birds[0].color

    def addCohesion(self):

        for bird in self.birds:
            coh = self.com - bird.position
            bird.speed += coh * self.adhesive

    def addAlignment(self):

        for bird in self.birds:
            aln = self.avel - bird.speed
            bird.speed += aln * self.alignive

    def addChill(self):
        bias = np.zeros(2)

        for bird in self.birds:
            bias = self.calculate_separation_bias(bird)
            bird.speed += bias * self.biassive

    def calculate_separation_bias(self, me):

        bias = np.zeros(2)
        dist = np.zeros(2)

        for bird in self.birds:
            if bird is me:
                continue

            dist = me.position - bird.position
            if np.linalg.norm(dist) < (me.size + bird.size)*2:
                bias += dist

        return bias

    def addRandom(self):

        for bird in self.birds:
            bird.speed += (np.random.rand(2) - 0.5 * np.ones(2)) * self.randosive

    def calculate_center_of_mass(self):
        com = np.zeros(2)

        total_mass = 0.
        for bird in self.birds:
            com += bird.mass * bird.position
            total_mass += bird.mass

        com /= total_mass

        return com

    def calculate_average_velocity(self):

        avel = np.zeros(2)

        for bird in self.birds:
            avel += bird.speed

        avel /= self.number_of_birds

        return avel

    def limit_bird_speed(self):

        maxspeed = 0.
        for bird in self.birds:
            maxspeed = np.max(np.abs(bird.speed))

            if maxspeed > self.speed_limit:
                factor = self.speed_limit / maxspeed
                bird.speed *= factor

    def addBuilding(self):
        # use addParticles instead
        height = np.random.rand() * 0.5 * self.height
        width = np.random.rand()  * 0.05 * self.width

        # starting right at the edge of the screen
        x = self.width
        y = self.height - height
        b = Building(x, y,width,height)

        # print(b)
        self.houses.append(b)

    def addPlane(self):
        # use addParticles instead
        height = np.random.rand() * 0.05 * self.height
        width = np.random.rand()  * 0.1 * self.width

        # starting right at the edge of the screen
        x = self.width
        y = np.random.rand() * 0.4 * self.height + height
        b = Plane(x, y, width,height, speed=(-np.random.rand(),0.))

        # print(b)
        self.planes.append(b)

    def birds_colliding(self):

        for bird in self.birds:
            if self.bird_within_building(bird):
                self.birds.remove(bird)
                self.dead_birds.append(bird)
                self.dead_birds[-1].speed[1] *= 0.50
                self.dead_birds[-1].speed[0] = 0.0

            if self.bird_within_plane(bird):
                self.birds.remove(bird)
                self.dead_birds.append(bird)
                self.dead_birds[-1].speed[1] *= 0.50
                self.dead_birds[-1].speed[0] = 0.0

                # self.number_of_birds -= 1

    def bird_within_building(self, bird):
        for house in self.houses:
            if sphere_within_rectangle(bird.position[0], bird.position[1], bird.size,
                                       house.position[0], house.position[1], house.width, house.height):
                return True

        return False

    # TODO: avoidable duplication
    def bird_within_plane(self, bird):
        for plane in self.planes:
            if sphere_within_rectangle(bird.position[0], bird.position[1], bird.size,
                                       plane.position[0], plane.position[1], plane.width, plane.height):
                return True

        return False

    def handle_input(self, key=None, value=None):
        if self.paused:
            return

        if key is None and value is None:
            pass
        elif key == 'master_speed':
            self.birds[0].speed += value * self.bird_speed_increase
        elif key == 'color_update':
            if value == 'backup_color':
                self.birds[0].color = self.backup_color
            elif value == 'green':
                self.birds[0].color = green


    def pause(self, paused):
        self.paused = paused

def sphere_within_rectangle(sphere_x, sphere_y, sphere_rad, rect_x, rect_y, rect_width, rect_height):
    # is bird.size == radius???

    # <= / >= or < / >
    if sphere_x + sphere_rad >= rect_x and \
       sphere_x - sphere_rad <= rect_x + rect_width:

        if sphere_y + sphere_rad >= rect_y and \
           sphere_y - sphere_rad <= rect_y + rect_height:

           return True

    return False

    #def update_scene(self):
    #    # move all immobiles according to self.advance

# TODO:
#   - initial bird pickup
#   - intermittent bird pickup from buildings
#   - planes
#   - faster rendering
#   - adaptive speed of winter
#   - adaptive height of buildings
