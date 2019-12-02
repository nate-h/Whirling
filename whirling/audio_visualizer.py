import math
import numpy as np
import librosa
import pygame as pg
from rx.subject.behaviorsubject import BehaviorSubject
from whirling.colors import COLORS
from whirling.primitives import Point
from whirling.audio_controller import AudioController
from whirling import audio_features

"""A class that spits out visuals
"""


# Needs update on song change
# Needs one time song loading/ processing
# Needs track location to load track
# Needs location in track on draw
# Possibly chunk data up so can minimize buffering.


class AudioVisualizer(object):
    def __init__(self, rect: pg.Rect, audio_controller: AudioController,
                 current_track: BehaviorSubject):
        self.rect = rect
        self.audio_controller = audio_controller
        self.track_audio_features = None

        self.debug_visuals = True
        self.debug_surface = pg.Surface((self.width, self.height))
        self.debug_window_number = None

        self.font = pg.font.Font(None, 25)

        # Register function for track changes.
        current_track.subscribe(self.current_track_change)

    ####################################
    # Props.
    ####################################

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

    ####################################
    # Game functions.
    ####################################

    def update(self):
        # Should job of this to queue up work?
        pass

    def draw(self, window):
        curr_time = self.audio_controller.get_time()

        if curr_time == -1:
            return

        if self.debug_visuals:
            self.draw_debug_visuals(window, curr_time)
        else:
            self.draw_framed_features(window, curr_time)

    ####################################
    # Visuals.
    ####################################

    def draw_framed_features(self, window, curr_time):
        # curr_frame = self.get_frame_number(curr_time)
        # print('%f    %d' % (curr_time, curr_frame))
        pass

    def draw_debug_visuals(self, window, curr_time):

        # Establish what portions of the track to visualize.
        seconds_worth = 10
        curr_window_number = math.floor(curr_time/seconds_worth)
        min_window_time = curr_window_number * seconds_worth
        max_window_time = (curr_window_number + 1) * seconds_worth
        min_window_frame = self.get_frame_number(min_window_time)
        max_window_frame = self.get_frame_number(max_window_time)

        if self.debug_window_number != curr_window_number:
            print('Update debug suface')
            print('Time: {}, window: {}, min_window_time: {} max_window_time: {}'.format(
                round(curr_time, 3), curr_window_number, min_window_time, max_window_time))
            self.debug_window_number = curr_window_number
            self.update_debug_visuals_surface(min_window_frame, max_window_frame)

        # Render debug visuals surface.
        window.blit(self.debug_surface, (0, 0))

        # Render line at current time.
        curr_percent = (curr_time-min_window_time) / seconds_worth
        margin = 0.05
        row_w = 1 - 2 * margin
        x = row_w * curr_percent + margin
        y1 = margin
        y2 = 1 - margin
        p1 = Point(x, y1)
        p2 = Point(x, y2)
        self.draw_line(window, p1, p2, (255, 255, 255), line_width=1)

    def update_debug_visuals_surface(self, min_window_frame, max_window_frame):

        # Reset surface.
        self.debug_surface.fill((0, 0, 0))

        num_frames = max_window_frame - min_window_frame
        signals = self.track_audio_features['audio_signals']
        sum_framed = sum([len(d['extracts']['framed']) for s,d in signals.items()])
        sum_framed_events = sum([len(d['extracts']['framed_events']) for s,d in signals.items()])
        num_rows = sum_framed + sum_framed_events

        # Plot properties.
        margin = 0.05
        row = 0
        text_height = .04
        row_h = (1-2*margin - num_rows*text_height)/num_rows
        row_growth = row_h + text_height
        r = 0.001
        row_w = 1 - 2*margin

        # Function to convert data to x, y values.
        def create_point_from(i, p):
            x = 1 - margin - (num_frames - i - 1)/ (num_frames - 1) * row_w
            y = row*row_growth + margin + row_h * (1 - p) + text_height
            return Point(x, y)

        def row_title(text):
            text_pos = Point(0.1, row*row_growth + margin + .01)
            self.draw_text(self.debug_surface, text, text_pos, color)


        for signal_name, signal_data in signals.items():
            framed = signal_data['extracts']['framed']
            framed_events = signal_data['extracts']['framed_events']

            for feature_name, data in framed.items():
                # Points spanning seconds_worth.
                pnts = data[min_window_frame: max_window_frame]
                color = COLORS[row][1]

                # Draw feature name text.
                row_title(signal_name + ' - ' + feature_name)
                last_p = None

                # Draw points for subset of feature data.
                for i, p in enumerate(pnts):
                    if i != 0:
                        p1 = create_point_from(i-1, last_p)
                        p2 = create_point_from(i, p)
                        self.draw_line(self.debug_surface, p1, p2, color)
                    last_p = p
                row += 1

            # Convert beat events to frames and then plot them.
            for feature_name, data in framed_events.items():
                beat_pnts = filter(
                    lambda x: min_window_frame <= x <= max_window_frame, data)
                beat_pnts = [p - min_window_frame for p in beat_pnts]
                pnts = np.zeros(max_window_frame - min_window_frame + 1)
                np.put(pnts, beat_pnts, np.ones(len(beat_pnts)))

                color = COLORS[row][1]

                # Draw feature name text.
                row_title(signal_name + ' - ' + feature_name)

                # Draw points for subset of feature data.
                for i, p in enumerate(pnts):
                    r = 0.004 if p > 0 else 0
                    point = create_point_from(i, p)
                    self.draw_circle(self.debug_surface, r, point, color)
                row += 1

    ####################################
    # Load data.
    ####################################

    def current_track_change(self, new_track):
        self.track_audio_features = audio_features.load_features(new_track)

        # Post processing. Converts events to framed events.
        self.post_process_audio_features()

    def post_process_audio_features(self):
        # Post processing. Converts events to framed events.
        # The reason I do this is so everything operates as a frame since
        # since that's the fundamental thing librosa returns.

        for _, data in self.track_audio_features['audio_signals'].items():
            events = data['extracts']['events']
            data['extracts']['framed_events'] = {
                k: [self.get_frame_number(e) for e in v] for k, v in events.items()
            }


    ####################################
    # Primitives.
    ####################################

    def draw_circle(self, surface, radius=0.1, center=Point(.5, .5), color=(20, 20, 20)):
        center = (int(self.width*center.x), int(self.height*center.y))
        radius = int(self.width * radius)
        pg.draw.circle(surface, color, center, radius)

    def draw_line(self, surface, p1=Point(.5, .5), p2=Point(.5, .5),
                  color=(20, 20, 20), line_width=2):
        p1 = (int(self.width*p1.x), int(self.height*p1.y))
        p2 = (int(self.width*p2.x), int(self.height*p2.y))
        pg.draw.line(surface, color, p1, p2, line_width)

    def draw_text(self, surface, text:str, text_pos=Point(.5, .5), color=(20, 20, 20)):
        text_pos = (int(self.width*text_pos.x), int(self.height*text_pos.y))
        text = self.font.render(text, True, color)
        surface.blit(text, text_pos)

    def create_linear_envelope(self, times, peak, slope):
        pass

    def time_lerp(self, begin_time, end_time, curr_time):
        # Returns a lerp from 1 -> 0 depending on how close curr_time is to
        # begin time or end time.
        diff = end_time - begin_time
        progress = curr_time - begin_time
        return max(1 - progress/diff, 0)