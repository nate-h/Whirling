from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
import pygame as pg
import OpenGL.GL as ogl
from enum import Enum
import numpy as np
from whirling import colors
from whirling.primitives import Rect
from whirling.ui_core import UIElement
from abc import ABC, abstractmethod


class UIVisualizerBase(UIElement, ABC):
    def __init__(self, rect=Rect(), **kwargs):
        super().__init__(rect=rect, **kwargs)

    def draw(self):
        self.draw_background()

    def update(self):
        pass

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height