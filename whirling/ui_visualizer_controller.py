from collections import OrderedDict
import os
import vlc
import time
from typing import List
import pygame as pg
from rx.subject.behaviorsubject import BehaviorSubject
from whirling.ui_core import UIDock, UIText, UIImage, UIButton, UIToggleButton
from whirling.ui_textures import WhirlingTextures
from whirling import colors
from whirling.primitives import Rect
import logging
from whirling.primitives import Point


class UIVisualizerController(UIDock):
    def __init__(self, current_visualizer: BehaviorSubject, rect: Rect,
                 bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        # Initialize pygame vars.
        self.font = pg.font.Font(None, 30)

        self.current_visualizer = current_visualizer

        self.whirling_textures = WhirlingTextures()
        self.initialize_elements()

    def initialize_elements(self):
        button_w = 50
        button_h = 50
        margin_x = 20
        self.elements = []

        def button_rect():
            count = len(self.elements)
            base_rect = Rect(0, button_h, button_w, 0)
            x = 10 + count*(button_w + margin_x)
            base_rect = base_rect.translate(x, 10)
            base_rect = base_rect.translate(self.rect.left, self.rect.bottom)
            return base_rect

        def initialize_button(texname, action):
            rect = button_rect()
            button = UIButton(rect, action,
                texset=self.whirling_textures, texname=texname,
                border_color=colors.WHITE)
            self.elements.append(button)
            return button

        # Initialize buttons
        self.prev_button = initialize_button('previous_arrow', self.prev_visual)
        self.next_button = initialize_button('next_arrow', self.next_visual)

        # Initialize current visualizer str.
        text_tup = (10 + self.rect.left, 60 + self.rect.bottom)
        self.visualizer_name = UIText('', text_tup, font_size=30)

        self.current_visualizer.subscribe(self.change_visualizer_name)

        self.elements.append(self.visualizer_name)

    def change_visualizer_name(self, text):
        self.visualizer_name.text = 'Visualizer: %s' % text

    def next_visual(self):
        print('Next visual')

    def prev_visual(self):
        print('Prev visual')

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()

    def handle_event(self, event):
        for e in self.elements:
            if hasattr(e, 'handle_event') and callable(e.handle_event):
                e.handle_event(event)
