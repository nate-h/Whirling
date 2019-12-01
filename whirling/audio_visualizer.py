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
        seconds_past = 2
        seconds_future = 1
        seconds_worth = seconds_past + seconds_future

        curr_frame = self.get_frame_number(curr_time + seconds_future)

        # Establish frame info.
        num_frames = self.get_frame_number(seconds_worth)
        oldest_frame = max(0, curr_frame - num_frames)


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
            self.draw_text(window, text, text_pos, color)


        for signal_name, signal_data in signals.items():
            framed = signal_data['extracts']['framed']
            framed_events = signal_data['extracts']['framed_events']

            for feature_name, data in framed.items():
                # Points spanning seconds_worth.
                pnts = data[oldest_frame: curr_frame]
                color = COLORS[row][1]

                # Draw feature name text.
                row_title(signal_name + ' - ' + feature_name)
                last_p = None

                # Draw points for subset of feature data.
                for i, p in enumerate(pnts):
                    if i != 0:
                        p1 = create_point_from(i-1, last_p)
                        p2 = create_point_from(i, p)
                        self.draw_line(window, p1, p2, color)
                    last_p = p
                row += 1

            # Convert beat events to frames and then plot them.
            for feature_name, data in framed_events.items():
                beat_pnts = filter(
                    lambda x: oldest_frame <= x <= curr_frame, data)
                beat_pnts = [p - oldest_frame for p in beat_pnts]
                pnts = np.zeros(curr_frame - oldest_frame + 1)
                np.put(pnts, beat_pnts, np.ones(len(beat_pnts)))

                color = COLORS[row][1]

                # Draw feature name text.
                row_title(signal_name + ' - ' + feature_name)

                # Draw points for subset of feature data.
                for i, p in enumerate(pnts):
                    r = 0.004 if p > 0 else 0
                    point = create_point_from(i, p)
                    self.draw_circle(window, r, point, color)
                row += 1

        # Render line at current time.
        x = row_w*seconds_past/seconds_worth + margin
        y1 = margin
        y2 = 1 - margin
        p1 = Point(x, y1)
        p2 = Point(x, y2)
        self.draw_line(window, p1, p2, (255, 255, 255), line_width=1)

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

    def draw_circle(self, window, radius=0.1, center=Point(.5, .5), color=(20, 20, 20)):
        center = (int(self.width*center.x), int(self.height*center.y))
        radius = int(self.width * radius)
        pg.draw.circle(window, color, center, radius)

    def draw_line(self, window, p1=Point(.5, .5), p2=Point(.5, .5),
                  color=(20, 20, 20), line_width=2):
        p1 = (int(self.width*p1.x), int(self.height*p1.y))
        p2 = (int(self.width*p2.x), int(self.height*p2.y))
        pg.draw.line(window, color, p1, p2, line_width)

    def draw_text(self, window, text:str, text_pos=Point(.5, .5), color=(20, 20, 20)):
        text_pos = (int(self.width*text_pos.x), int(self.height*text_pos.y))
        text = self.font.render(text, True, color)
        window.blit(text, text_pos)

    def create_linear_envelope(self, times, peak, slope):
        pass

    def time_lerp(self, begin_time, end_time, curr_time):
        # Returns a lerp from 1 -> 0 depending on how close curr_time is to
        # begin time or end time.
        diff = end_time - begin_time
        progress = curr_time - begin_time
        return max(1 - progress/diff, 0)