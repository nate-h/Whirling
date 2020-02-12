import math
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling import colors
from whirling.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from whirling.ui_core import UIText


class DebugVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

    def draw(self):
        super().draw()

        self.draw_debug_visuals_surface()

    def draw_debug_visuals_surface(self):

        if self.track_audio_features is None:
            return

        # Establish what portions of the track to visualize.
        curr_time = self.audio_controller.get_time()
        seconds_worth = 10
        curr_window_number = math.floor(curr_time/seconds_worth)
        min_window_time = curr_window_number * seconds_worth
        max_window_time = (curr_window_number + 1) * seconds_worth
        min_window_frame = self.get_frame_number(min_window_time)
        max_window_frame = self.get_frame_number(max_window_time)

        num_frames = max_window_frame - min_window_frame
        signals = self.track_audio_features['audio_signals']
        sum_framed = sum([len(d['extracts']['framed']) for s,d in signals.items()])
        sum_framed_events = sum([len(d['extracts']['framed_events']) for s,d in signals.items()])
        num_rows = sum_framed + sum_framed_events

        # Plot properties.
        row_num = 0
        row_height = 50
        row_gap = 50

        for signal_name, signal_data in signals.items():
            framed = signal_data['extracts']['framed']
            framed_events = signal_data['extracts']['framed_events']

            for feature_name, data in framed.items():
                # Points spanning seconds_worth.
                pnts = data[min_window_frame: max_window_frame]

                if len(pnts) == 0:
                    continue

                # Draw points for subset of feature data.
                self.plot_signal(pnts, row_num, row_height, row_gap, feature_name)
                row_num += 1


            # # Convert beat events to frames and then plot them.
            # for feature_name, data in framed_events.items():
            #     beat_pnts = filter(
            #         lambda x: min_window_frame <= x <= max_window_frame, data)
            #     beat_pnts = [p - min_window_frame for p in beat_pnts]
            #     pnts = np.zeros(max_window_frame - min_window_frame + 1)
            #     np.put(pnts, beat_pnts, np.ones(len(beat_pnts)))

            #     color = COLORS[row][1]

            #     # Draw feature name text.
            #     row_title(signal_name + ' - ' + feature_name)

            #     # Draw points for subset of feature data.
            #     for i, p in enumerate(pnts):
            #         r = 0.004 if p > 0 else 0
            #         point = create_point_from(i, p)
            #         self.draw_circle(self.debug_surface, r, point, color)
            #     row += 1

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

        # TODO: not memoized!
        pos = (pl, pb + dh + row_gap/10)
        UIText(title, pos, font_size=20, font_color=color).draw()

        # Draw checkerboard.
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

    def draw_line(self, point, size, color):
        x,y = point
        s = size/2.0
        glVertex2f(x-s, y-s)      # bottom left point
        glVertex2f(x+s, y-s)      # bottom right point
        glVertex2f(x+s, y+s)      # top right point
        glVertex2f(x-s, y+s)      # top left point

    def draw_rect(self, point, size, color):
        glColor3f(*color)
        x,y = point
        s = size/2.0
        glVertex2f(x-s, y-s)      # bottom left point
        glVertex2f(x+s, y-s)      # bottom right point
        glVertex2f(x+s, y+s)      # top right point
        glVertex2f(x-s, y+s)      # top left point
