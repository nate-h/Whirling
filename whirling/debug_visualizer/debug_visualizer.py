import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling.ui_visualizer_base import UIVisualizerBase


class CheckerboardVisualizer(UIVisualizerBase):
    def __init__(self, rect, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, **kwargs)

    def draw(self):
        pass
