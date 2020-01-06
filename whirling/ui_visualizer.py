from whirling.ui_core import UIElement, UIAnchorPositions, UIDock
from whirling import colors


class UIVisualizer(UIDock):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

    def draw(self):
        super().draw()
