"""Whirling
Defines the UI to switch the visuals.
"""

import logging
import pygame as pg
from whirling.ui_core.ui_core import UIDock, UIText, UIButton
from whirling.ui_core.ui_textures import WhirlingTextures
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect
from whirling.visualizers import VISUALIZERS
from whirling.store import Store


class UIVisualizerController(UIDock):
    """Defines the UI to switch the visuals."""

    def __init__(self, rect: Rect,
                 bg_color=colors.CLEAR, border_color=colors.BLACK):
        """Initialize the class."""

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
                         border_color=border_color)

        # Initialize pygame vars.
        self.font = pg.font.Font(None, 30)

        # Switch to using the first visual.
        self.current_visualizer_bs = Store.get_instance().current_visualizer_bs
        plan_visualizers = set(Store.get_instance().plan['visualizers'].keys())
        self.visualizers = [
            v[0] for v in VISUALIZERS if v[0] in plan_visualizers
        ]
        self.next_visual()

        self.whirling_textures = WhirlingTextures()
        self.initialize_elements()

    def initialize_elements(self):
        """Initialize visual elements contained in this component."""
        button_w = 50
        button_h = 50
        margin_x = 20
        self.elements = []

        def button_rect():
            """Create rect for buttons."""
            count = len(self.elements)
            base_rect = Rect(0, button_h, button_w, 0)
            x = 10 + count*(button_w + margin_x)
            base_rect = base_rect.translate(x, 10)
            base_rect = base_rect.translate(self.rect.left, self.rect.bottom)
            return base_rect

        def initialize_button(texname, action):
            """Create a button with a text label."""
            rect = button_rect()
            button = UIButton(rect, action,
                              texset=self.whirling_textures,
                              texname=texname,
                              border_color=colors.WHITE)
            self.elements.append(button)
            return button

        # Initialize buttons
        self.prev_button = initialize_button('previous_arrow', self.prev_visual)
        self.next_button = initialize_button('next_arrow', self.next_visual)

        # Initialize current visualizer str.
        text_tup = (10 + self.rect.left, 60 + self.rect.bottom)
        self.visualizer_name = UIText('', text_tup, font_size=30)

        self.current_visualizer_bs.subscribe(self.change_visualizer_name)

        self.elements.append(self.visualizer_name)

    def change_visualizer_name(self, text):
        """Handles changes to the visualizer name."""
        self.visualizer_name.text = f'Visualizer: {text}'

    def next_visual(self):
        """Changes the visualizer to the next in line."""
        # If no visuals, quit.
        if len(self.visualizers) == 0:
            logging.info('No visualizers found. Quitting.')
            pg.quit()
            quit()

        # If no visualizer set, set to first one in vis list.
        current_visualizer: str = self.current_visualizer_bs.value
        if current_visualizer == "":
            self.current_visualizer_bs.on_next(self.visualizers[0])
        # Else find next one.
        else:
            idx = self.visualizers.index(current_visualizer)
            vis = self.visualizers[(idx + 1) % len(self.visualizers)]
            self.current_visualizer_bs.on_next(vis)

    def prev_visual(self):
        """Changes the visualizer to the previous in line."""
        # If no visuals, quit.
        if len(self.visualizers) == 0:
            logging.info('No visualizers found. Quitting.')
            pg.quit()
            quit()

        # If no visualizer set, set to first one in vis list.
        current_visualizer: str = self.current_visualizer_bs.value
        if current_visualizer == "":
            self.current_visualizer_bs.on_next(self.visualizers[0])
        # Else find next one.
        else:
            idx = self.visualizers.index(current_visualizer)
            vis = self.visualizers[(idx - 1) % len(self.visualizers)]
            self.current_visualizer_bs.on_next(vis)

    def draw(self):
        """Draw all the elements contained in this component."""
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()

    def handle_event(self, event):
        """Test and handle events a child component may have."""
        for e in self.elements:
            if hasattr(e, 'handle_event') and callable(e.handle_event):
                e.handle_event(event)
