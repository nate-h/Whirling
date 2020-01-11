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
        count = 0
        margin_x = 20

        base_rect = Rect(0, button_h, button_w, 0)
        self.prev = UIImage(self.whirling_textures, 'prev',
            base_rect.translate(10 + count*(button_w + margin_x), 10))
        count += 1

        self.play = UIImage(self.whirling_textures, 'play',
            base_rect.translate(10 + count*(button_w + margin_x), 10))
        count += 1

        self.elements = [
            self.prev,
            self.play
        ]

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()
