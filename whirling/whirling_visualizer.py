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
    def __init__(self, rect, audio_controller: WhirlingAudioController,
                 current_track: BehaviorSubject):
        self.rect = rect
        self.audio_controller = audio_controller

        current_track.subscribe(self.load_track)

    def update(self):
        pass
    def draw(self, window):
        #print(self.audio_controller.player.get_time())
        pass

    def load_track(self, new_track):
        print('librosa load: %s' % new_track)