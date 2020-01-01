#!/usr/bin/env python

"""This example demonstrates creating an image with Numeric
python, and displaying that through SDL. You can look at the
method of importing numeric and pygame.surfarray. This method
will fail 'gracefully' if it is not available.
I've tried mixing in a lot of comments where the code might
not be self explanatory, nonetheless it may still seem a bit
strange. Learning to use numeric for images like this takes a
bit of learning, but the payoff is extremely fast image
manipulation in python.

Just so you know how this breaks down. For each sampling of
time, 30% goes to each creating the gradient and blitting the
array. The final 40% goes to flipping/updating the display surface

If using an SDL version at least 1.1.8 the window will have
no border decorations.

The code also demonstrates use of the timer events."""


import os
import pygame
from pygame.locals import *
import gradients
from gradients import vertical as gradient2
import sys
from numpy import oldnumeric as Numeric
import numpy as np


size = 800, 600
if len(sys.argv) > 2:
    size = (int(sys.argv[1]), int(sys.argv[2]))


timer = 0


def stopwatch(message=None):
    "simple routine to time python code"
    global timer
    if not message:
        timer = pygame.time.get_ticks()
        return
    now = pygame.time.get_ticks()
    runtime = (now - timer)/1000.0 + .001
    print(message, runtime, ('seconds\t(%.2ffps)' % (1.0/runtime)))
    timer = now


def VertGrad3D(surf, topcolor, bottomcolor):
    "creates a new 3d vertical gradient array"
    topcolor = np.array(topcolor, copy=0)
    bottomcolor = np.array(bottomcolor, copy=0)
    diff = bottomcolor - topcolor
    width, height = surf.get_size()
    # create array from 0.0 to 1.0 triplets
    column = np.arange(height, dtype=np.float64)/height    # 0 -> 1
    column = np.repeat(column[:, np.newaxis], [3], 1)      # Copy that array 3 time  shape=600x3
    # create a single column of gradient
    column = topcolor + (diff * column).astype(np.int64)   # Linear interp from topcolor to bottom
                                                           # color based on 0 -> 1 value shape=600x3
    # make the column a 3d image column by adding X
    column = column.astype(np.uint8)[np.newaxis, :, :]     # 1x600x3
    #3d array into 2d array
    column = pygame.surfarray.map_array(surf, column)      # 1x600
    # stretch the column into a full image
    return np.resize(column, (width, height))


def DisplayGradient(surf):
    "choose random colors and show them"
    colors = np.random.randint(0, 255, (2, 3))
    stopwatch()
    grade = VertGrad3D(surf, colors[0], colors[1])
    stopwatch('numeric Gradient:')
    pygame.surfarray.blit_array(surf, grade)
    pygame.display.flip()


def DisplayGradient2(surf):
    colors = np.random.randint(0, 255, (2, 4))
    stopwatch()
    grade = gradient2(size, colors[0], colors[1])
    stopwatch(' pygame Gradient:')
    surf.blit(grade, (size[0]/2, 0))
    pygame.display.flip()


def main():
    pygame.init()
##    size = 600, 400
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode(size, NOFRAME, 0)
##    screen = pygame.display.set_mode(size, NOFRAME|pygame.SRCALPHA)

    pygame.event.set_blocked(MOUSEMOTION) #keep our queue cleaner
    pygame.time.set_timer(USEREVENT, 1000)

    while 1:
        event = pygame.event.wait()
        if event.type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
            break
        elif event.type == USEREVENT:
            DisplayGradient(screen)
            DisplayGradient2(screen)
            print('-------------')


if __name__ == '__main__':
    main()

