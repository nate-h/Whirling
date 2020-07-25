import re
import copy
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

        self.store = Store.get_instance()
        self.sub = self.store.is_plan_loaded_bs.subscribe(
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

        # Reset data and return if nothing to work with.
        self.data = None
        if not is_loaded:
            return

        data_wanted = self.store.plan['visualizers'][self.name]['signals']
        self.data = copy.deepcopy(data_wanted)
        signals = self.store.plan_output['signals']

        for signal_name, signal_data in data_wanted.items():
            for transformer_name, transformer_data in signal_data.items():

                # Attach features to data.
                if transformer_name == 'features':
                    for f_name, use in transformer_data.items():
                        if use:
                            self.data[signal_name][transformer_name][f_name] = \
                                signals[signal_name][transformer_name][f_name]

                # Attach spectrogram to data.
                if transformer_name == 'spectrograms':
                    self.data[signal_name]['D'] = signals[signal_name]['D']

                    for s_name, use in transformer_data.items():
                        if use:
                            self.data[signal_name][transformer_name][s_name] = \
                                signals[signal_name][transformer_name][s_name]

        # Perform any derived class specific post processing.
        self.post_process_data()

    def post_process_data(self):
        pass

    @property
    def name(self):
        return re.sub( '(?<!^)(?=[A-Z])', '_', self.__class__.__name__.replace(
            'Visualizer', '')).lower()

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def sr(self):
        return self.store.plan['metadata']['sr']

    @property
    def hop_length(self):
        return self.store.plan['metadata']['hop_length']

    def get_frame_number(self, time):
        return audio_features.get_frame_number(time, self.sr, self.hop_length)
