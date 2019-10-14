from whirling_audio_controller import WhirlingAudioController

"""A class that spits out visuals
"""


# Needs update on song change
# Needs one time song loading/ processing
# Needs track location to load track
# Needs location in track on draw
# Possibly chunk data up so can minimize buffering.


class WhirlingVisualizer(object):
    def __init__(self, rect, audio_controller: WhirlingAudioController):
        self.rect = rect
        self.audio_controller = audio_controller
    def update(self):
        pass
    def draw(self, window):
        print(self.audio_controller.player.get_time())

    def on_song_load(self):
        pass