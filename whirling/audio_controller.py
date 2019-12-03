from collections import OrderedDict
from rx.subject.behaviorsubject import BehaviorSubject
import pygame as pg
import vlc
import os
import time
import logging
from whirling import ui_core
from whirling.primitives import Point


"""The audio controller for whirling.
"""


class AudioController():
    def __init__(self, rect, music_tracks, current_track: BehaviorSubject):
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
        self.offset = Point(rect.left, rect.top)

        # Initialize background and buttons.
        self.bg_color = (20, 20, 20)
        self.bg = self.relative_rect(0, 0, rect.width, rect.height)
        self.initialize_buttons()

        # Time string
        self.current_time_loc = (self.offset.x + 10, self.offset.y + 10)
        self.track_name_loc = (self.bg.width - 50, 20)

    def relative_rect(self, x, y, w, h):
        rect = pg.Rect(x, y, w, h)
        return rect.move(self.offset.x, self.offset.y)

    def initialize_buttons(self):
        # Play button
        states = OrderedDict([
            ('play', {'action': self.play}),
            ('pause', {'action': self.pause})
        ])
        ph = self.bg.height*0.6
        pw = ph*2
        x = self.bg.width/2 - pw/2
        y = self.bg.height/2 - ph/2
        play_rect = self.relative_rect(x, y, pw, ph)
        self.play_button = ui_core.ToggleButton(states, play_rect)

        # Prev/Next buttons
        pnh = self.bg.height*0.5
        pnw = pnh*2
        x = self.bg.width/2
        y = self.bg.height/2 - pnh/2
        prev_offset_x = x - pw/2 - 20 - pnw
        next_offset_x = x + pw/2 + 20
        prev_rect = self.relative_rect(prev_offset_x, y, pnw, pnh)
        next_rect = self.relative_rect(next_offset_x, y, pnw, pnh)
        self.prev_button = ui_core.Button('Prev', self.prev, prev_rect)
        self.next_button = ui_core.Button('Next', self.next, next_rect)

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

    def draw_current_time(self, window):
        time_str = self.get_pretty_time_string()
        text_surface = self.font.render(time_str, True, pg.Color('white'))
        window.blit(text_surface, self.current_time_loc)

    def draw_song_name(self, window):
        text_surface = self.font.render(self.track_name, True, pg.Color('white'))
        loc = self.track_name_loc
        moved_track_name_loc = (loc[0] - text_surface.get_width(), loc[1])
        window.blit(text_surface, moved_track_name_loc)

    def draw(self, window):
        pg.draw.rect(window, self.bg_color, self.bg)
        self.prev_button.draw(window)
        self.play_button.draw(window)
        self.next_button.draw(window)
        self.draw_current_time(window)
        self.draw_song_name(window)

    def play(self):
        logging.info('Play')
        self.player.play()

    def pause(self):
        logging.info('Pause')
        self.player.pause()

    def toggle_play(self):
        logging.info('Toggle play')
        self.play_button.perform_action()

    def adjust_time_by(self, seconds):
        if not self.is_playing:
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

        # TODO: Shouldn't short circuit here and need to rewrite time interpolation code so it returns
        #       the correct time when paused.
        if not self.is_playing:
            return -1

        curr_time = self.player.get_time() * .001

        if self.last_play_time == curr_time and self.last_play_time != 0:
            curr_time += time.time() - self.last_play_time_global
        else:
            self.last_play_time = curr_time
            self.last_play_time_global = time.time()

        return curr_time

    def update(self):
        pass

    def handle_event(self, event):
        self.prev_button.handle_event(event)
        self.play_button.handle_event(event)
        self.next_button.handle_event(event)
