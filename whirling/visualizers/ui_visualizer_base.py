from abc import ABC, abstractmethod
from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
from whirling.ui_core.primitives import Rect
from whirling.ui_core.ui_core import UIElement
from whirling.ui_audio_controller import UIAudioController
from whirling.signal_transformers import audio_features
from whirling.store import Store


class UIVisualizerBase(UIElement, ABC):
    def __init__(self, rect=Rect(), audio_controller: UIAudioController=None, **kwargs):
        super().__init__(rect=rect, **kwargs)

        self.audio_controller = audio_controller
        self.data = None

        Store.get_instance().is_plan_loaded_bs.subscribe(
            self.on_data_loaded_change)

    def draw(self):
        self.draw_background()
        self.draw_border()

        if self.data:
            self.draw_visuals()
        #else:
        #    Render loading screen.

    @abstractmethod
    def draw_visuals(self):
        pass

    def update(self):
        pass

    def on_data_loaded_change(self, is_loaded):
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
