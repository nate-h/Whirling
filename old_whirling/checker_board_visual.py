import math
import random
import numpy as np
import pygame as pg

# http://geodynamics.usc.edu/~becker/teaching/557/problem_sets/problem_set_fd_2dheat.pdf
# Rate of energy transfer to another node

class CheckerBoardVisual():
    def __init__(self, displayw, displayh):
        self.width = displayw
        self.height = displayh

        self.cols = 75
        self.side_length = math.floor(self.width / self.cols)
        self.rows = math.floor(self.height / self.side_length)

        self.offset_x = (self.width - self.cols* self.side_length) / 2
        self.offset_y = (self.height - self.rows* self.side_length) / 2

        self.surface = pg.Surface((self.side_length * self.cols, self.side_length * self.rows))

        print('rows: %d' % self.rows)
        print('cols: %d' % self.cols)

        self.data_r = np.zeros((self.rows, self.cols))
        self.data_g = np.zeros((self.rows, self.cols))
        self.data_b = np.zeros((self.rows, self.cols))

        self.randomize_data()

    def randomize_data(self):
        random_color = lambda t: random.randint(0, 255)
        vfunc = np.vectorize(random_color)
        self.data_r = vfunc(self.data_r)
        self.data_r = np.repeat(np.repeat(self.data_r, self.side_length, axis=0), self.side_length, axis=1)

        self.data_g = vfunc(self.data_g)
        self.data_g = np.repeat(np.repeat(self.data_g, self.side_length, axis=0), self.side_length, axis=1)

        self.data_b = vfunc(self.data_b)
        self.data_b = np.repeat(np.repeat(self.data_b, self.side_length, axis=0), self.side_length, axis=1)

        self.data_rgb = np.dstack((self.data_r, self.data_g, self.data_b))
        print(self.data_rgb.shape)

    def update(self):
        pass

    def draw(self, window):
        self.surface.fill((0, 0, 0))

        surf = pg.surfarray.make_surface(self.data_rgb)

        window.blit(surf, (self.offset_x, self.offset_y))

    def convert_1_to_255(self):
        pass