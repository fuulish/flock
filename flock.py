#!/usr/bin/env python

import pygame
import boid
from collections import namedtuple
from events import Events

from display import Display

import numpy as np

from constants import red, green, blue, white, black, color, display_mode

# is DEAD
# import psyco
# psyco.full()

from pygame.locals import FULLSCREEN, DOUBLEBUF
flags = FULLSCREEN | DOUBLEBUF
# flags = DOUBLEBUF

if __name__ == '__main__':
    events = Events()

    my_disp = Display(flags)

    number_of_birds = 20

    env = boid.Flock(my_disp.mode.width, my_disp.mode.height)

    env.addBirds(n=number_of_birds, density=10.)
    env.addFunctions(['move', 'bounce', 'collide', 'cohere', 'chill', 'align'])
    #env.addFunctions(['move', 'bounce', 'collide', 'cohere', 'chill', 'align', 'randomize'])
    env.elasticity = 1.

    running = True
    win = False

    display_updates = {
        'birds' : env.particles,
        'sitting' : env.sitting,
        'dead_birds' : env.dead_birds,
        'houses' : env.houses,
        'planes' : env.planes,
        'death_zone' : env.death_zone,
    }

    winning_dist = 5000

    while running:

        todo = events.handle()
        for key in todo:
            env.handle_input(key=key, value=todo[key])

        running = todo['running']
        paused = todo['paused']

        env.pause(paused)

        # TODO: use background image instead
        # screen.fill(background_color)
        if not paused:
            alive = env.update()

        # TODO: use either an object for houses or a property for death_zone
        display_updates.update({ 'death_zone' : env.death_zone, 'progress' : env.distance_travelled })

        my_disp.update(display_updates)

        # print(alive)
        if alive == 0:
            running = False
            win = False
            print('All birdies are gone, man!')
        elif env.distance_travelled >= winning_dist:
            # first, disallow adding of buildings and planes and add another distance to travel to safety
            if env.allow_new_entities:
                env.allow_new_entities = False
            elif len(env.houses) == 0 and len(env.planes) == 0:
                running = False
                win = True

        # pygame.display.flip()
        # pygame.display.update()

    my_disp.reset()

    if win:
        my_disp.victory()
    else:
        my_disp.defeat()

    running = True
    while running:
        todo = events.handle()
        running = todo['running']

    print('Travelled %i distance units with %i birds left' %(env.distance_travelled, alive))

    my_disp.quit()
