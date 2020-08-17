import pygame

from constants import red, green, blue, white, black, color, display_mode

background_color = white

class Display(object):
    def __init__(self, flags):
        pygame.display.init()
        infoObject = pygame.display.Info()
        self.mode = display_mode(infoObject.current_w, infoObject.current_h)
        #screen = pygame.display.set_mode(mode)
        self.screen = pygame.display.set_mode(self.mode, flags)
        self.screen.set_alpha(None)

        pygame.display.set_caption('Flock U')

        self.screen.fill(background_color)
        pygame.display.flip()

        self.bgimg = self.screen.copy()

        self.oldrects = []

        self.font_size = self.mode.height // 20

        pygame.font.init()
        self.final_font = pygame.font.SysFont('Comic Sans MS', self.font_size)
        self.progress_font = pygame.font.SysFont('Comic Sans MS', self.font_size // 3)

    def update(self, display_updates):

        rects = self.new_rectangles(display_updates)

        activerects = rects + self.oldrects
        #activerects = filter(bool, activerects)

        pygame.display.update(activerects)
        self.oldrects = rects[:]

        for rect in rects:
            self.screen.blit(self.bgimg, rect, rect)

    def new_rectangles(self, display_updates):

        rects = []

        for p in display_updates['birds']:
            rects.append(self.display_alive_bird(p))

        for p in display_updates['sitting']:
            rects.append(self.display_alive_bird(p))

        for p in display_updates['dead_birds']:
            rects.append(self.display_dead_bird(p))

        for b in display_updates['houses']:
            rects.append(self.display_rect_building(b))

        for p in display_updates['planes']:
            rects.append(self.display_rect_plane(p))

        rects.append(self.display_death_zone(display_updates['death_zone']))
        rects.append(self.progress_indicator(display_updates['progress']))

        return rects

    def quit(self):
        pygame.display.quit()

    def display_alive_bird(self, particle):
        return pygame.draw.circle(self.screen, particle._color,
                    (int(particle.position[0]), int(particle.position[1])),
                    particle._size, particle._thickness)

    def display_dead_bird(self, particle):
        return pygame.draw.circle(self.screen, particle._color,
                    (int(particle.position[0]), int(particle.position[1])),
                    particle._size, 1)

    def display_rect_building(self, building):
        return self.display_rect_shape(building)

    def display_rect_plane(self, plane):
        return self.display_rect_shape(plane)

    def display_rect_shape(self, rect):
        return pygame.draw.rect(self.screen, black, (rect.position[0], rect.position[1], rect.width, rect.height) , 1)

    def display_death_zone(self, zone):
        return pygame.draw.line(self.screen, black, (zone, self.mode.height), (zone, 0), 1 )

    def reset(self):
        self.screen.fill(background_color)

    def progress_indicator(self, progress):
        text = '%i' %(int(progress))
        position = (0,0)
        return self.text_on_screen(text, position, font='progress')

    def victory(self):
        self.reset()

        text = 'You Win'
        position = ((self.mode[0] - len(text)*self.font_size)/2, (self.mode[1] - self.font_size)/2)
        self.text_on_screen(text, position)

        pygame.display.flip()

    def defeat(self):
        self.reset()

        text = 'You Loose!'
        position = ((self.mode[0] - len(text)*self.font_size)/2, (self.mode[1] - self.font_size)/2)
        self.text_on_screen(text, position)

        pygame.display.flip()

    def text_on_screen(self, text, position, font='final'):
        if font == 'final':
            textsurface = self.final_font.render(text, False, (0, 0, 0))
        elif font == 'progress':
            textsurface = self.progress_font.render(text, False, (0, 0, 0))

        return self.screen.blit(textsurface,position)
