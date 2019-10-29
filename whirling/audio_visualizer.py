import librosa
import pygame as pg
from primitives import Point
from audio_controller import AudioController
import audio_features
from rx.subject.behaviorsubject import BehaviorSubject
from colors import COLORS

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
        self.current_track_audio_features = None
        self.debug_visuals = True

        # Register function for track changes.
        current_track.subscribe(self.current_track_change)

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def sr(self):
        return self.current_track_audio_features['metadata']['sr']

    @property
    def hop_length(self):
        return self.current_track_audio_features['metadata']['hop_length']

    def update(self):
        # Should job of this to queue up work?
        pass

    def draw(self, window):
        curr_time = self.audio_controller.get_time()

        if curr_time == -1:
            return

        self.draw_framed_features(window, curr_time)

        return

        beats = audio_features.get_events_at_time(
            self.current_track_audio_features, curr_time)
        if len(beats) > 0:
            beat = beats[0]
            percent = self.time_lerp(beat[0], beat[1], curr_time)
            radius = 0.1 * percent
            self.draw_circle(window, radius=radius)

    def draw_framed_features(self, window, curr_time):
        curr_frame = audio_features.get_frame_number(
            curr_time, self.sr, self.hop_length)
        print('%f    %d' % (curr_time, curr_frame))

        if self.debug_visuals:
            self.draw_debug_visuals(window, curr_frame)

    def draw_debug_visuals(self, window, curr_frame):
        # Get number of frames to extract data from.
        seconds_worth = 5
        number_of_frames = audio_features.get_frame_number(
            seconds_worth, self.sr, self.hop_length)

        framed = self.current_track_audio_features['framed']
        frame_times = framed['frame_times']
        row = 0

        for k, data in framed.items():
            if k == 'frame_times':
                continue
            # Points spanning seconds_worth.
            pnts = data[max(0, curr_frame - number_of_frames): curr_frame]
            h = 0.1
            w = 0.8
            r = 0.001
            margin = 0.1
            delta = w/number_of_frames
            color = COLORS[row][1]

            # if len(pnts) == 215:
            #     import pdb; pdb.set_trace()

            for i, p in enumerate(pnts):
                x = 1 - margin - (number_of_frames - i - 1)/ (number_of_frames - 1) * w
                y = row*0.2 + 2*margin + h * (p - 1)
                center = Point(x, y)
                self.draw_circle(window, r, center, color)
            row += 1

    def current_track_change(self, new_track):
        cache_exists = audio_features.cache_exists(new_track)
        if self.use_cache and cache_exists:
            self.current_track_audio_features = audio_features.load_features(new_track)
        else:
            self.current_track_audio_features = audio_features.generate_features(new_track)

    def draw_circle(self, window, radius=0.1, center=Point(.5, .5), color=(20, 20, 20),):
        center = (int(self.width*center.x), int(self.height*center.y))
        radius = int(self.width * radius)
        pg.draw.circle(window, color, center, radius)

    def create_linear_envelope(self, times, peak, slope):
        pass

    def time_lerp(self, begin_time, end_time, curr_time):
        # Returns a lerp from 1 -> 0 depending on how close curr_time is to
        # begin time or end time.
        diff = end_time - begin_time
        progress = curr_time - begin_time
        return max(1 - progress/diff, 0)