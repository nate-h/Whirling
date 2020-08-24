"""Whirling
A visualizer that renders all plan specified spectrograms.
"""

import math
from OpenGL.GL import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLU import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLUT import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
import OpenGL.GL.shaders
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect
from whirling.visualizers.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from whirling.ui_core.ui_core import UIText
from whirling.visualizers import spectrogram


class SpectrogramVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        # The size of the spectrogram clip in seconds.
        self.seconds_worth: int = 8

        # What clip of full spectrogram we are looking at.
        self.spec_window = None

        self.specs = []
        self.text_elements = {}

    def draw_visuals(self):

        curr_time = self.audio_controller.get_time()

        # Create spectrogram if it doesn't exist for this spec window.
        if self.spec_window != math.floor(curr_time / self.seconds_worth):
            self.create_spectrograms(curr_time)

        if len(self.specs) > 0:
            for s in self.specs:
                s.draw()
            for _label, text_element in self.text_elements.items():
                text_element.draw()

        # Draw time indicator.
        self.draw_time_indicator(curr_time)

    def create_spectrograms(self, curr_time):

        # Ditch old specs.
        self.specs = []

        # Grab spectrogram and what portions we're going to limit it to.
        num_rows = len(self.data)
        row_gap = 50

        if len(self.data) == 0:
            logging.info('No spectrograms to view.')
            return

        row_height = (self.height - num_rows*row_gap) / num_rows

        self.spec_window = math.floor(curr_time / self.seconds_worth)
        min_window_time = self.spec_window * self.seconds_worth
        max_window_time = (self.spec_window + 1) * self.seconds_worth
        min_window_frame = self.get_frame_number(min_window_time)
        max_window_frame = self.get_frame_number(max_window_time)

        if max_window_frame == 0:
            return

        # Create the spectrograms.
        row_num = 0
        for signal_name, s_obj in self.data.items():
            bottom = row_num * (row_gap + row_height) + self.rect.bottom
            top = bottom + row_height
            log_db_s = s_obj['spectrograms']['custom_log_db']
            log_db_s_clip = log_db_s[min_window_frame: max_window_frame, :]
            spec_rect = Rect(self.rect.left, top, self.rect.right, bottom)
            spec = spectrogram.Spectrogram(spec_rect, log_db_s_clip)
            self.specs.append(spec)

            # Draw signal name text above spectrogram.
            color = colors.WHITE
            pos = (self.rect.left + 10, top + 10)
            self.render_text(signal_name, pos, color)
            row_num += 1

    def draw_time_indicator(self, curr_time):

        curr_window_number = math.floor(curr_time/self.seconds_worth)
        min_window_time = curr_window_number * self.seconds_worth
        max_window_time = (curr_window_number + 1) * self.seconds_worth

        if max_window_time == 0:
            return
        fraction = (curr_time - min_window_time) / (
            max_window_time - min_window_time)
        x = self.width * fraction + self.rect.left
        glBegin(GL_LINES)
        glColor3fv(colors.GRAY)
        glVertex2f(x, self.rect.top)
        glVertex2f(x, self.rect.bottom)
        glEnd()

    def render_text(self, title, pos, color):
        """Generate text if doesn't exist then render it."""
        if title not in self.text_elements:
            self.text_elements[title] = UIText(
                title, pos, font_size=20, font_color=color)
