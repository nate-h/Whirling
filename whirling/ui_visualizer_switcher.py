from rx.subject.behaviorsubject import BehaviorSubject
from whirling.ui_core.ui_core import UIDock
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect
from whirling.visualization_manager import VISUALIZERS
from whirling.ui_audio_controller import UIAudioController
from whirling.store import Store


class UIVisualizerSwitcher(UIDock):
    def __init__(self, plan, audio_controller: UIAudioController,
                 rect: Rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        self.visualizer = None
        self.track_audio_features = None
        self.audio_controller = audio_controller
        self.plan = plan

        # Subscribe to visualizer and track changes.
        Store.get_instance().current_visualizer_bs.subscribe(
            self.on_visualizer_change)
        Store.get_instance().current_track_bs.subscribe(
            self.current_track_change)

    def get_visualizer_rect(self):
        padding_percent = .03
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

    def draw(self):
        super().draw()

        self.visualizer.draw()

    def find_visualizer_class(self, vis_name):
        return list(filter(lambda x: x[0] == vis_name, VISUALIZERS))[0][1]

    def on_visualizer_change(self, vis_name):
        print('Changing visualizer: %s ' % vis_name)
        rect = self.get_visualizer_rect()
        self.visualizer = self.find_visualizer_class(vis_name)(
            rect, self.audio_controller) #, border_color=colors.RED)

        # Copy audio features over to visualizer.
        if self.visualizer:
            self.visualizer.track_audio_features = self.track_audio_features

    def current_track_change(self, new_track):
        # self.track_audio_features = audio_features.load_features(
        #     new_track, self.plan)

        # Copy audio features over to visualizer.
        self.visualizer.track_audio_features = self.track_audio_features
