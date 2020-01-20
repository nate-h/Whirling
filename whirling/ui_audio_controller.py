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


class UIAudioController(UIDock):
    def __init__(self, music_tracks: List[str], current_track: BehaviorSubject,
        rect: Rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect=rect, bg_color=bg_color,
            border_color=border_color)

        # Setup player.
        self.track_num = 0
        self.player = None
        self.current_track = current_track
        self.music_tracks = music_tracks
        self.current_track.on_next(self.music_tracks[self.track_num])
        self.current_track.subscribe(self.change_song)

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
        self.elements = []

        play_states = OrderedDict([
            ('play', {'action': self.play}),
            ('pause', {'action': self.pause})
        ])

        def button_rect():
            count = len(self.elements)
            base_rect = Rect(0, button_h, button_w, 0)
            x = 10 + count*(button_w + margin_x)
            base_rect = base_rect.translate(x, 10)
            return base_rect

        def initialize_button(texname, action):
            rect = button_rect()
            button = UIButton(rect, self.rw,
                texset=self.whirling_textures, texname=texname,
                border_color=colors.WHITE)
            self.elements.append(button)
            return button

        # Initialize buttons
        self.rw_button = initialize_button('rw', self.rw)
        self.prev_button = initialize_button('prev', self.prev)
        self.play_button = UIToggleButton(button_rect(), play_states,
            texset=self.whirling_textures, border_color=colors.WHITE)
        self.elements.append(self.play_button)
        self.next_button = initialize_button('next', self.next)
        self.ffw_button = initialize_button('ffw', self.ffw)

        # Initialize current time str.
        self.current_time = UIText('0.00', (10, 60), font_size=30)
        self.elements.append(self.current_time)

    def handle_event(self, event):
        for e in self.elements:
            if hasattr(e, 'handle_event') and callable(e.handle_event):
                e.handle_event(event)

    def draw(self):
        self.draw_background()
        self.draw_border(bottom=False, left=False, right=False)

        # Draw all elements this component owns.
        for e in self.elements:
            e.draw()

    def x__init__(self, rect, music_tracks, current_track: BehaviorSubject):
        # Setup player.
        self.track_num = 0
        self.player = None
        self.current_track = current_track
        self.music_tracks = music_tracks
        self.current_track.on_next(self.music_tracks[self.track_num])
        self.current_track.subscribe(self.change_song)

        # Vars needed to track current time.
        self.last_play_time = 0
        self.last_play_time_global = 0

    def change_song(self, new_track):
        logging.info('New track: %s', new_track)
        is_playing = self.player and self.player.is_playing()
        if is_playing:
            self.player.stop()
        self.player = vlc.MediaPlayer(new_track)
        self.player.audio_set_volume(100)
        if is_playing:
            self.player.play()

    @property
    def is_playing(self):
        return self.player and self.player.is_playing()

    @property
    def center(self):
        return Point(self.offset.x + self.bg.width/2, self.offset.y + self.bg.height/2)

    @property
    def track_name(self):
        return os.path.basename(self.music_tracks[self.track_num])

    def draw_song_name(self, window):
        text_surface = self.font.render(self.track_name, True, pg.Color('white'))
        loc = self.track_name_loc
        moved_track_name_loc = (loc[0] - text_surface.get_width(), loc[1])
        window.blit(text_surface, moved_track_name_loc)

    def play(self):
        logging.info('Play')
        self.player.play()

        # Save this out because poor resolution of vlc's get time.
        # Check get_time for more info.
        curr_time = self.player.get_time() * .001
        self.last_play_time = curr_time
        self.last_play_time_global = time.time()

    def pause(self):
        logging.info('Pause')
        self.player.pause()

        # Save this out because poor resolution of vlc's get time.
        # Check get_time for more info.
        curr_time = self.player.get_time() * .001
        self.last_play_time = curr_time
        self.last_play_time_global = time.time()

    def toggle_play(self):
        logging.info('Toggle play')
        self.play_button.perform_action()

    def ffw(self):
        self.adjust_time_by(2)

    def rw(self):
        self.adjust_time_by(-2)

    def adjust_time_by(self, seconds):
        if self.player is None:
            return
        logging.info('Adjusting time by %d seconds ', seconds)
        curr_time = self.player.get_time()
        proposed_time = curr_time + 1000*seconds
        max_time = self.player.get_length()
        realistic_proposed_time = min(max(proposed_time, 0), max_time)
        self.player.set_time(realistic_proposed_time)

    def prev(self):
        count = len(self.music_tracks)
        self.track_num = (self.track_num - 1 + count) % count
        self.current_track.on_next(self.music_tracks[self.track_num])

    def next(self):
        count = len(self.music_tracks)
        self.track_num = (self.track_num + 1) % count
        self.current_track.on_next(self.music_tracks[self.track_num])

    def get_pretty_time_string(self):
        length = round(self.player.get_length()/1000, 1)
        time = round(self.player.get_time()/1000, 1)
        return '%s / %s' % (time, length)

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
            self.last_play_time = curr_time
            self.last_play_time_global = time.time()

        return curr_time

    def update(self):
        time_str = self.get_pretty_time_string()
        self.current_time.text = time_str
