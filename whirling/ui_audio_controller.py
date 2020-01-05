from whirling.ui_core import UIElement, UIAnchorPositions
from whirling import colors

class UIDock(UIElement):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        self.rect = rect
        self.position = rect.position

        # Initialize base class.
        super().__init__(bg_color, border_color,
            anchor_position=UIAnchorPositions.BOTTOM_LEFT)

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def draw(self):
        super().draw()

class UIAudioController(UIDock):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

    def draw(self):
        super().draw()
