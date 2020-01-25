from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
import pygame as pg
import OpenGL.GL as ogl
from enum import Enum
import numpy as np
from whirling import colors
from whirling.primitives import Rect
from abc import ABC, abstractmethod

class UIVisualizerBase(ABC):
    def __init__(
        self, rect=Rect()
    ):
        super().__init__(rect=rect)

    def draw(self):
        self.draw_background()

    def update(self):
        pass

    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass