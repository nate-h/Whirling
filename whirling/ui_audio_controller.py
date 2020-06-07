import os
import time
import logging
from collections import OrderedDict
from typing import List
import vlc
import pygame as pg
from whirling.ui_core.ui_core import UIDock, UIText, UIButton, UIToggleButton
from whirling.ui_core.ui_textures import WhirlingTextures
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect
from whirling.store import Store


class UIAudioController(UIDock):
    def __init__(self, music_tracks: List[str], rect: Rect,
                 bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        # Setup player.
        self.volume = 100
        self.track_num = 0
        self.player = None
        self.store = Store.get_instance()
        self.music_tracks = music_tracks
        self.store.current_track_bs.on_next(self.music_tracks[self.track_num])
        self.store.current_track_bs.subscribe(self.on_track_change)

        # Vars needed to track current time.
        self.last_play_time = 0
        self.last_play_time_global = 0

        # Initialize pygame vars.
        self.font = pg.font.Font(None, 30)

        self.whirling_textures = WhirlingTextures()
        self.initialize_elements()

    def initialize_elements(self):
        button_w = 50
        button_h = 50
        margin_x = 20
        gap = 0
        self.elements = []

        play_states = OrderedDict([
            ('play', {'action': self.play}),
            ('pause', {'action': self.pause})
        ])

        def button_rect():
            count = len(self.elements)
            base_rect = Rect(0, button_h, button_w, 0)
            x = 10 + count*(button_w + margin_x) + gap
            base_rect = base_rect.translate(x, 10)
            return base_rect

        def initialize_button(texname, action):
            rect = button_rect()
            button = UIButton(rect, action,
                texset=self.whirling_textures, texname=texname,
                border_color=colors.WHITE)
            self.elements.append(button)
            return button

        # Initialize buttons
        # self.rw_button = initialize_button('rw', self.rw_key_down)
        self.prev_button = initialize_button('prev', self.prev)
        self.play_button = UIToggleButton(button_rect(), play_states,
            texset=self.whirling_textures, border_color=colors.WHITE)
        self.elements.append(self.play_button)
        self.next_button = initialize_button('next', self.next)
        # self.ffw_button = initialize_button('ffw', self.ffw_key_down)

        # Add volume buttons and text.
        gap += 50
        self.volume_up_button = initialize_button('up_arrow', self.volume_up)
        self.volume_down_button = initialize_button('down_arrow', self.volume_down)
        self.volume_text = UIText('Volume: %s' % self.volume, (
            self.volume_up_button.rect.left, 60), font_size=30)
        self.elements.append(self.volume_text)

        # Initialize current time str.
        self.current_time = UIText('0.00', (10, 60), font_size=30)
        self.elements.append(self.current_time)

    def handle_event(self, event):
        for e in self.elements:
            if hasattr(e, 'handle_event') and callable(e.handle_event):
                e.handle_event(event)

    def update(self):
        time_str = self.get_pretty_time_string()
        self.current_time.text = time_str

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()

    def on_track_change(self, new_track):
        is_playing = self.player and self.player.is_playing()
        if is_playing:
            self.player.stop()
        self.player = vlc.MediaPlayer(new_track)
        self.player.audio_set_volume(self.volume)
        if is_playing:
            self.player.play()

    def volume_up(self):
        self.set_volume(self.volume + 10)

    def volume_down(self):
        self.set_volume(self.volume - 10)

    def set_volume(self, volume):
        self.volume = max(min(volume, 100), 0)
        self.player.audio_set_volume(self.volume)
        self.volume_text.text = 'Volume: %s' % self.volume

    @property
    def is_playing(self):
        return self.player and self.player.is_playing()

    @property
    def track_name(self):
        return os.path.basename(self.music_tracks[self.track_num])

    def play(self):
        logging.info('Play')
        self.player.play()

        # Save this out because poor resolution of vlc's get time.
        # Check get_time for more info.
        self.reset_time_vars()

    def pause(self):
        logging.info('Pause')
        self.player.pause()

        # Save this out because poor resolution of vlc's get time.
        # Check get_time for more info.
        self.reset_time_vars()

    def toggle_play(self):
        logging.info('Toggle play')
        self.play_button.perform_action()

    def ffw_key_down(self):
        if self.player is None:
            return
        self.player.set_rate(20)

    # def rw_key_down(self):
    #     if self.player is None:
    #         return
    #     self.player.set_rate(-5)

    def playback_speed_key_up(self):
        if self.player is None:
            return
        self.player.set_rate(1)

    def prev(self):
        count = len(self.music_tracks)
        self.track_num = (self.track_num - 1 + count) % count
        self.store.current_track_bs.on_next(self.music_tracks[self.track_num])

    def next(self):
        count = len(self.music_tracks)
        self.track_num = (self.track_num + 1) % count
        self.store.current_track_bs.on_next(self.music_tracks[self.track_num])

    def get_pretty_time_string(self):
        length_seconds = round(self.player.get_length()/1000, 1)
        time_seconds = round(self.get_time(), 1)
        return '%s / %s' % (time_seconds, length_seconds)

    def get_time(self):
        # This exists because vlcs default get time updates only a couple
        # of times per second.
        if not self.is_playing:
            return self.player.get_time() * .001

        curr_time = self.player.get_time() * .001

        # If player hasn't updated it's time, update an internal timer.
        # Else reset that internal timer and return updated player time.
        if self.last_play_time == curr_time and self.last_play_time != 0:
            curr_time += time.time() - self.last_play_time_global
        else:
            self.reset_time_vars()

        return curr_time

    def reset_time_vars(self):
        curr_time = self.player.get_time() * .001
        self.last_play_time = curr_time
        self.last_play_time_global = time.time()
