import SeedAMG8833
import pygame
import os
import math
import time

import numpy as np
from scipy.interpolate import griddata

from colour import Color

#low range of the sensor (this will be blue on the screen)
MINTEMP = 26

#high range of the sensor (this will be red on the screen)
MAXTEMP = 31

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')

#initialize the sensor
sensor = SeedAMG8833.AMG8833()

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]


#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#let the sensor initialize
time.sleep(.1)

pixels = sensor.read_temp()
pixels = [map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]

#perdorm interpolation
bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')

#draw everything
data_img = np.zeros((bicubic.shape[0],bicubic.shape[1],3), dtype=np.uint8)
for ix, row in enumerate(bicubic):
    for jx, pixel in enumerate(row):
        r,g,b = colors[constrain(int(pixel), 0, COLORDEPTH- 1)]
        data_img[jx,ix] = [r,g,b]
# pygame.display.update()
data_img = np.rot90(data_img, k=1)
return data_img
	
