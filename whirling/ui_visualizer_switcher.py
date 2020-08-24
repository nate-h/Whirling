"""Whirling
A wrapper element to contain the current visualizer and contains methods
to switch between them.
"""

from whirling.ui_core.ui_core import UIDock
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect
from whirling.visualizers import find_visualizer_class
from whirling.ui_audio_controller import UIAudioController
from whirling.store import Store


class UIVisualizerSwitcher(UIDock):
    """A wrapper element class to contain the current visualizer and contains
    methods to switch between them.
    """
    def __init__(self, plan, audio_controller: UIAudioController,
                 rect: Rect, bg_color=colors.CLEAR, border_color=colors.BLACK):
        """Initialize the class."""
        super().__init__(rect=rect, bg_color=bg_color,
                         border_color=border_color)

        self.visualizer = None
        self.audio_controller = audio_controller
        self.plan = plan

        # Subscribe to visualizer and track changes.
        Store.get_instance().current_visualizer_bs.subscribe(
            self.on_visualizer_change)

    def get_visualizer_rect(self):
        """Return rect the current visualizer should render to."""
        padding_percent = .03
        padding = self.rect.width * padding_percent
        return Rect(
            self.rect.left + padding,
            self.rect.top - padding,
            self.rect.right - padding,
            self.rect.bottom + padding
        )

    def draw(self):
        """Draw the visualizer."""
        super().draw()
        self.visualizer.draw()

    def on_visualizer_change(self, vis_name):
        """Switch out current visualizer with another."""
        print('Changing visualizer: %s ' % vis_name)
        rect = self.get_visualizer_rect()

        # TODO: Get a __del__ working. Likely circular reference causing it
        #       not to fire.
        if self.visualizer:
            self.visualizer.sub.dispose()

        self.visualizer = find_visualizer_class(vis_name)(
            rect, self.audio_controller) #, border_color=colors.RED)
