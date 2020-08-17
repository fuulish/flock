import pygame
import numpy as np

class Events(object):
    def __init__(self):
        pass
        self.paused = False

    def handle(self, **kwargs):

        running = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # press-press mechanics
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = (True, False)[self.paused]

        master_speed = np.zeros(2, dtype='int')
        pressed_keys = pygame.key.get_pressed()

        cnt = 0
        if pressed_keys[pygame.K_RIGHT]:
            master_speed[0] += 1
            cnt += 1

        if pressed_keys[pygame.K_LEFT]:
            master_speed[0] -= 1
            cnt += 1

        if pressed_keys[pygame.K_DOWN]:
            master_speed[1] += 2
            cnt += 1

        if pressed_keys[pygame.K_UP]:
            master_speed[1] -= 1
            cnt += 1


        if pressed_keys[pygame.K_LCTRL] and pressed_keys[pygame.K_f]:
            pygame.display.toggle_fullscreen()

        if pressed_keys[pygame.K_LCTRL] and pressed_keys[pygame.K_q]:
            running = False

        if cnt == 0:
            color_update = 'backup_color'
        elif cnt > 0:
            color_update = 'green'

        ret = {
            'master_speed' : master_speed,
            'color_update' : color_update,
            'running' : running,
            'paused' : self.paused,
        }

        return ret
