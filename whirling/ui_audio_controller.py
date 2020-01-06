from whirling.ui_core import UIAnchorPositions, UIDock, UIButton, UIText, UIImage
from whirling.ui_textures import WhirlingTextures
from whirling import colors
from whirling.primitives import Rect


class UIAudioController(UIDock):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        self.whirling_textures = WhirlingTextures()
        self.initialize_elements()

    def initialize_elements(self):
        #self.play = UIButton('Play', (offset_x, 85, 0), font_size=50)
        button_w = 50
        button_h = 50
        base_rect = Rect(0, button_h, button_w, 0)
        self.next = UIImage(self.whirling_textures, 'next',
            base_rect.translate(10, 10))

        self.elements = [
            self.next
        ]

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()
