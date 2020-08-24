"""Whirling
A visualizer to view all plan specified audio features.
"""

import math
import numpy as np
from OpenGL.GL import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLU import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLUT import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from whirling.ui_core import colors
from whirling.visualizers.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from whirling.ui_core.ui_core import UIText
from whirling.signal_transformers import audio_features


class DebugVisualizer(UIVisualizerBase):
    """A visualizer to view feature extractions for signals."""
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)
        self.text_elements = {}

    def draw_visuals(self):

        # Establish what portions of the track to visualize.
        curr_time = self.audio_controller.get_time()
        seconds_worth = 10
        curr_window_number = math.floor(curr_time/seconds_worth)
        min_window_time = curr_window_number * seconds_worth
        max_window_time = (curr_window_number + 1) * seconds_worth
        min_window_frame = self.get_frame_number(min_window_time)
        max_window_frame = self.get_frame_number(max_window_time)

        if max_window_frame == 0:
            return

        signals = self.data

        # Count number of features we have so we can scale the rows properly.
        num_rows = 0
        for _, s_obj in self.data.items():
            for _, f_obj in s_obj['features'].items():
                if f_obj is not None:
                    num_rows += 1

        # Plot properties.
        row_num = 0
        row_gap = 50
        row_height = (self.height - num_rows * row_gap)/num_rows

        for signal_name, s_obj in signals.items():
            for feature_name, f_data in s_obj['features'].items():
                if f_data is None:
                    continue

                flavor = audio_features.function_listing(feature_name)['flavor']
                title = "%s - %s" % (signal_name, feature_name)

                # Plot continuous events like onset_strengths.
                if flavor == 'continuous':
                    # Points spanning seconds_worth.
                    pnts = f_data[min_window_frame: max_window_frame]

                    # Draw points for subset of feature data.
                    self.plot_signal(pnts, row_num, row_height, row_gap, title)

                # Plot discrete events like onsets.
                if flavor == 'discrete':
                    beat_pnts = filter(
                        lambda x: min_window_frame <= x <= max_window_frame, f_data)
                    beat_pnts = [p - min_window_frame for p in beat_pnts]
                    pnts = np.zeros(max_window_frame - min_window_frame + 1)
                    np.put(pnts, beat_pnts, np.ones(len(beat_pnts)))

                    # Draw points for subset of feature data.
                    self.plot_discrete_signal(pnts, row_num, row_height, row_gap, title)

                row_num += 1

        self.draw_time_indicator(curr_time, min_window_time, max_window_time)

    def draw_time_indicator(self, curr_time, min_time, max_time):
        if max_time == 0:
            return
        fraction = (curr_time - min_time) / (max_time - min_time)
        x = self.width * fraction + self.rect.left
        glBegin(GL_LINES)
        glColor3fv(colors.GRAY)
        glVertex2f(x, self.rect.top)
        glVertex2f(x, self.rect.bottom)
        glEnd()

    def plot_signal(self, signal_segment, row_num, row_height, row_gap, title):

        dx = self.width/ len(signal_segment)
        dh = row_height
        pb = self.rect.bottom + row_num * (row_height+row_gap)
        pl = self.rect.left
        color = list(colors.COLORS.values())[row_num]

        # Generate text if doesn't exist then render it.
        pos = (pl, pb + dh + row_gap/10)
        self.render_text(title, pos, color)

        # Draw lines.
        glBegin(GL_LINES)
        glColor3fv(color)
        for i, y1 in enumerate(signal_segment):
            x1 = i*dx
            x2 = (i+1)*dx
            y2 = signal_segment[i+1]
            if i == len(signal_segment) - 2:
                break
            glVertex2f(pl + x1, pb + y1*dh)
            glVertex2f(pl + x2, pb + y2*dh)
        glEnd()

    def plot_discrete_signal(self, points, row_num, row_height, row_gap, title):

        dx = self.width/ len(points)
        dh = row_height
        pb = self.rect.bottom + row_num * (row_height+row_gap)
        pl = self.rect.left
        color = list(colors.COLORS.values())[row_num]

        # Generate text if doesn't exist then render it.
        pos = (pl, pb + dh + row_gap/10)
        self.render_text(title, pos, color)

        # Draw points.
        glPointSize(5)
        glBegin(GL_POINTS)
        glColor3fv(color)
        for i, y1 in enumerate(points):
            if y1 > 0:
                x1 = i*dx
                glVertex2f(pl + x1, pb + y1*dh*0.7)
        glEnd()

    def render_text(self, title, pos, color):
        """Generate text if doesn't exist then render it."""
        if title not in self.text_elements:
            self.text_elements[title] = UIText(
                title, pos, font_size=20, font_color=color)
        self.text_elements[title].draw()
