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
                 current_track: BehaviorSubject, use_cache=False):
        self.rect = rect
        self.audio_controller = audio_controller
        self.use_cache=use_cache
        self.curr_track_audio_features = None
        self.debug_visuals = True
        self.font = pg.font.Font(None, 30)

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
        return self.curr_track_audio_features['metadata']['sr']

    @property
    def hop_length(self):
        return self.curr_track_audio_features['metadata']['hop_length']

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

        self.draw_framed_features(window, curr_time)

    ####################################
    # Visuals.
    ####################################

    def draw_framed_features(self, window, curr_time):
        curr_frame = self.get_frame_number(curr_time)
        print('%f    %d' % (curr_time, curr_frame))

        if self.debug_visuals:
            self.draw_debug_visuals(window, curr_frame)

    def draw_debug_visuals(self, window, curr_frame):
        # Get number of frames to extract data from.
        seconds_worth = 5
        num_frames = self.get_frame_number(seconds_worth)

        framed = self.curr_track_audio_features['framed']
        framed_events = self.curr_track_audio_features['framed_events']
        frame_times = framed['frame_times']
        oldest_frame = max(0, curr_frame - num_frames)

        # Plot properties.
        row = 0
        row_growth = 0.15
        h = 0.1
        w = 0.8
        r = 0.001
        margin = 0.1

        for feature_name, data in framed.items():
            if feature_name == 'frame_times':
                continue
            # Points spanning seconds_worth.
            pnts = data[oldest_frame: curr_frame]
            color = COLORS[row][1]

            # Draw feature name text.
            text_pos = Point(0.1, row*row_growth + margin - 0.03)
            self.draw_text(window, feature_name, text_pos, color)

            # Draw points for subset of feature data.
            for i, p in enumerate(pnts):
                x = 1 - margin - (num_frames - i - 1)/ (num_frames - 1) * w
                y = row*row_growth + margin + h * (1 - p)
                center = Point(x, y)
                self.draw_circle(window, r, center, color)
            row += 1

        # Convert beat events to frames and then plot them.
        for feature_name, data in framed_events.items():
            beat_pnts = filter(lambda x: oldest_frame <= x <= curr_frame, data)
            beat_pnts = [p - oldest_frame for p in beat_pnts]
            pnts = np.zeros(curr_frame - oldest_frame + 1)
            np.put(pnts, beat_pnts, np.ones(len(beat_pnts)))

            color = COLORS[row][1]

            # Draw feature name text.
            text_pos = Point(0.1, row*row_growth + margin - 0.03)
            self.draw_text(window, feature_name, text_pos, color)

            # Draw points for subset of feature data.
            for i, p in enumerate(pnts):
                r = 0.004 if p > 0 else 0
                x = 1 - margin - (num_frames - i - 1)/ (num_frames - 1) * w
                y = row*row_growth + margin + h * (1 - p)
                center = Point(x, y)
                self.draw_circle(window, r, center, color)
            row += 1

    ####################################
    # Load data.
    ####################################

    def current_track_change(self, new_track):
        cache_exists = audio_features.cache_exists(new_track)
        if self.use_cache and cache_exists:
            self.curr_track_audio_features = audio_features.load_features(new_track)
        else:
            self.curr_track_audio_features = audio_features.generate_features(new_track)

        # Post processing. Converts events to framed events.
        self.post_process_audio_features()

    def post_process_audio_features(self):
        # Post processing. Converts events to framed events.
        # The reason I do this is so everything operates as a frame since
        # since that's the fundamental thing librosa returns.
        events = self.curr_track_audio_features['events']
        self.curr_track_audio_features['framed_events'] = {
            k: [self.get_frame_number(e) for e in v] for k, v in events.items()
        }


    ####################################
    # Primitives.
    ####################################

    def draw_circle(self, window, radius=0.1, center=Point(.5, .5), color=(20, 20, 20)):
        center = (int(self.width*center.x), int(self.height*center.y))
        radius = int(self.width * radius)
        pg.draw.circle(window, color, center, radius)

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