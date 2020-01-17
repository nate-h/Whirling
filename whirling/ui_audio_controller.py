from whirling.ui_core import UIDock, UIText, UIImage, UIButton
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
        button_w = 50
        button_h = 50
        count = 0
        margin_x = 20

        def button_rect(i):
            base_rect = Rect(0, button_h, button_w, 0)
            return base_rect.translate(10 + count*(button_w + margin_x), 10)

        self.prev = UIImage(button_rect(count), self.whirling_textures, 'prev')
        count += 1

        self.play = UIImage(button_rect(count), self.whirling_textures, 'play')
        count += 1

        self.next = UIButton(button_rect(count), lambda x: print(x),
            texset=self.whirling_textures, texname='next',
            border_color=colors.WHITE)
        count += 1

        self.elements = [
            self.prev,
            self.play,
            #self.next,
        ]

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()
