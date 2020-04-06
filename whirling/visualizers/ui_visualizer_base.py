from abc import ABC
from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
from whirling.ui_core.primitives import Rect
from whirling.ui_core.ui_core import UIElement
from whirling.ui_audio_controller import UIAudioController
from whirling.signal_transformers import audio_features


class UIVisualizerBase(UIElement, ABC):
    def __init__(self, rect=Rect(), audio_controller: UIAudioController=None, **kwargs):
        super().__init__(rect=rect, **kwargs)

        self.audio_controller = audio_controller
        self.track_audio_features = None

    def draw(self):
        self.draw_background()
        self.draw_border()

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
