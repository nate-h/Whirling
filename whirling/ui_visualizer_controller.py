from whirling.ui_core import UIElement, UIDock
from whirling import colors


class UIVisualizerController(UIDock):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)
