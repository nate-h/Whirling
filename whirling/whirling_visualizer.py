import time
import librosa
import pygame as pg
from whirling_primitives import Point
from whirling_audio_controller import WhirlingAudioController
from rx.subject.behaviorsubject import BehaviorSubject

"""A class that spits out visuals
"""


# Needs update on song change
# Needs one time song loading/ processing
# Needs track location to load track
# Needs location in track on draw
# Possibly chunk data up so can minimize buffering.


class WhirlingVisualizer(object):
    def __init__(self, rect: pg.Rect, audio_controller: WhirlingAudioController,
                 current_track: BehaviorSubject):
        self.rect = rect
        self.audio_controller = audio_controller

        current_track.subscribe(self.load_track)

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
        curr_time = self.audio_controller.player.get_time() / 1000
        beats = self.get_beats(curr_time)
        if len(beats) > 0:
            self.draw_circle(window)

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