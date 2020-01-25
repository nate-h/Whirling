from rx.subject.behaviorsubject import BehaviorSubject
from whirling.ui_core import UIElement, UIDock
from whirling import colors
from whirling.primitives import Rect
from whirling.checkerboard_visualizer.checkerboard_visualizer import CheckerboardVisualizer


class UIVisualizerSwitcher(UIDock):
    def __init__(self, current_visualizer: BehaviorSubject, rect: Rect,
            bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        current_visualizer.subscribe(self.change_visualizer)

        self.visualizers = {
            'debug': '',
            'checkerboard': CheckerboardVisualizer,
        }
        self.visualizer = None

    def draw(self):
        super().draw()

    def change_visualizer(self, next_visualizer_name):
        print('Changing visualizer: %s ' % next_visualizer_name)
        self.visualizer = self.visualizers[next_visualizer_name]
