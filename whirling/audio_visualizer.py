import time
import librosa
import pygame as pg
from primitives import Point
from audio_controller import AudioController
from rx.subject.behaviorsubject import BehaviorSubject

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

        # Register function on track change.
        current_track.subscribe(self.current_track_change)

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def update(self):
        # Should job of this to queue up work?
        pass

    def draw(self, window):
        curr_time = self.audio_controller.get_time()
        beats = self.get_beats(curr_time)
        if len(beats) > 0:
            beat = beats[0]
            percent = self.time_lerp(beat[0], beat[1], curr_time)
            radius = 0.1 * percent
            #print('%3f %3f %3f %3f' % (beat[0], beat[1], curr_time, percent))
            self.draw_circle(window, radius=radius)

    def current_track_change(self, new_track):
        cache_exists = False
        if self.use_cache and cache_exists:
            self.current_track_audio_features = self.load_cache(new_track)
        else:
            self.load_track(new_track)

    def load_cache(self):
        pass

    def load_track(self, new_track):
        start_time = time.time()
        print('librosa load: %s' % new_track)
        y, sr = librosa.load(new_track)
        self.process_beats(y, sr)
        print('Current time to process song:  %f' % (time.time() - start_time))

    def draw_circle(self, window, radius=0.1, color=(20, 20, 20), center=Point(.5, .5)):
        center = (int(self.width*center.x), int(self.height*center.y))
        radius = int(self.width * radius)
        pg.draw.circle(window, color, center, radius)

    def process_beats(self, y, sr):
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
        # 4. Convert the frame indices of beat events into timestamps
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        sustain = 0.2
        self.beats = [(b, b + sustain) for b in beat_times]

    def get_beats(self, curr_time):
        # See what beats should be played at curr_time
        return [b for b in self.beats if curr_time >= b[0] and curr_time < b[1]]

    def create_linear_envelope(times, peak, slope):
        pass

    def time_lerp(self, begin_time, end_time, curr_time):
        # Returns a lerp from 1 -> 0 depending on how close curr_time is to
        # begin time or end time.
        diff = end_time - begin_time
        progress = curr_time - begin_time
        return max(1 - progress/diff, 0)