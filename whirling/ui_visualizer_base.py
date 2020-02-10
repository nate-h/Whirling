from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
import pygame as pg
import OpenGL.GL as ogl
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
from whirling import colors
from whirling.primitives import Rect
from whirling.ui_core import UIElement
from whirling import audio_features
from whirling.ui_audio_controller import UIAudioController


class UIVisualizerBase(UIElement, ABC):
    def __init__(self, rect=Rect(), audio_controller: UIAudioController=None, **kwargs):
        super().__init__(rect=rect, **kwargs)

        self.audio_controller = audio_controller
        self.track_audio_features = None

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

    @property
    def sr(self):
        return self.track_audio_features['metadata']['sr']

    @property
    def hop_length(self):
        return self.track_audio_features['metadata']['hop_length']

    def get_frame_number(self, time):
        return audio_features.get_frame_number(time, self.sr, self.hop_length)
