from rx.subject.behaviorsubject import BehaviorSubject
from whirling.ui_core import UIElement, UIDock
from whirling import colors
from whirling.primitives import Rect
from whirling.VisualizationManager import visualizers
from whirling.ui_audio_controller import UIAudioController
from whirling import audio_features


class UIVisualizerSwitcher(UIDock):
    def __init__(self, current_visualizer: BehaviorSubject,
                 current_track: BehaviorSubject, audio_controller: UIAudioController,
                 rect: Rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        self.visualizer = None
        self.audio_controller = audio_controller

        current_visualizer.subscribe(self.change_visualizer)

        # Register function for track changes.
        current_track.subscribe(self.current_track_change)

    def get_visualizer_rect(self):
        padding_percent = .05
        padding = self.rect.width * padding_percent
        return Rect(
            self.rect.left + padding,
            self.rect.top - padding,
            self.rect.right - padding,
            self.rect.bottom + padding
        )

    @property
    def sr(self):
        return self.track_audio_features['metadata']['sr']

    @property
    def hop_length(self):
        return self.track_audio_features['metadata']['hop_length']

    def get_frame_number(self, time):
        return audio_features.get_frame_number(time, self.sr, self.hop_length)

    def draw(self):
        super().draw()

        self.visualizer.draw()

    def find_visualizer_class(self, vis_name):
        return list(filter(lambda x: x[0] == vis_name, visualizers))[0][1]

    def change_visualizer(self, vis_name)   :
        print('Changing visualizer: %s ' % vis_name)
        rect = self.get_visualizer_rect()
        self.visualizer = self.find_visualizer_class(vis_name)(
            rect, self.audio_controller, border_color=colors.RED)

    def current_track_change(self, new_track):
        self.track_audio_features = audio_features.load_features(new_track)

        # Post processing. Converts events to framed events.
        self.post_process_audio_features()

        # Copy audio features over to visualizer.
        self.visualizer.track_audio_features = self.track_audio_features

    def post_process_audio_features(self):
        # Post processing. Converts events to framed events.
        # The reason I do this is so everything operates as a frame since
        # since that's the fundamental thing librosa returns.

        for _, data in self.track_audio_features['audio_signals'].items():
            events = data['extracts']['events']
            data['extracts']['framed_events'] = {
                k: [self.get_frame_number(e) for e in v] for k, v in events.items()
            }
