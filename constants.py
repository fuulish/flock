
from collections import namedtuple

color = namedtuple('color',  'red, green, blue')

white = color(255, 255, 255)
black = color(0, 0, 0)

red = color(255, 0, 0)
green = color(0, 255, 0)
blue = color(0, 0, 255)

display_mode = namedtuple('display', 'width, height')
