import pygame as pg
import vlc
from collections import OrderedDict, namedtuple
import whirling_ui as UI
import os

MUSIC_TRACKS = [
    'data/Christian Löffler - Mare/Christian Löffler - Mare - 02 Haul (feat. Mohna).mp3',
    'data/bensound-buddy.mp3'
]


Point = namedtuple('Point', ['x', 'y'])


######################################################

class AudioController():
    def __init__(self, rect, music_tracks):
        self.track_num = 0
        self.offset = Point(rect.left, rect.top)
        self.music_tracks = music_tracks
        self.player = vlc.MediaPlayer(self.music_tracks[self.track_num])
        self.font = pg.font.Font(None, 30)

        self.bg_color = (20, 20, 20)
        self.bg = self.relative_rect(0, 0, rect.width, rect.height)

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
        self.play_button = UI.ToggleButton(states, play_rect)

        # Prev/Next buttons
        pnh = self.bg.height*0.5
        pnw = pnh*2
        x = self.bg.width/2
        y = self.bg.height/2 - pnh/2
        prev_offset_x = x - pw/2 - 20 - pnw
        next_offset_x = x + pw/2 + 20
        prev_rect = self.relative_rect(prev_offset_x, y, pnw, pnh)
        next_rect = self.relative_rect(next_offset_x, y, pnw, pnh)
        self.prev_button = UI.Button('Prev', self.prev, prev_rect)
        self.next_button = UI.Button('Next', self.next, next_rect)

        # Time string
        self.current_time_loc = (self.offset.x + 10, self.offset.y + 10)
        self.track_name_loc = (self.bg.width - 50, 50)

    def relative_rect(self, x, y, w, h):
        rect = pg.Rect(x, y, w, h)
        return rect.move(self.offset.x, self.offset.y)

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
        print('Play')
        self.player.play()

    def pause(self):
        print('Pause')
        self.player.pause()

    def prev(self):
        is_playing = self.player.is_playing
        self.player.stop()
        count = len(self.music_tracks)
        self.track_num = (self.track_num - 1 + count) % count
        self.player = vlc.MediaPlayer(self.music_tracks[self.track_num])
        if is_playing:
            self.player.play()

    def next(self):
        is_playing = self.player.is_playing
        self.player.stop()
        count = len(self.music_tracks)
        self.track_num = (self.track_num + 1) % count
        self.player = vlc.MediaPlayer(self.music_tracks[self.track_num])
        if is_playing:
            self.player.play()

    def get_pretty_time_string(self):
        length = round(self.player.get_length()/1000, 1)
        time = round(self.player.get_time()/1000, 1)
        return '%s / %s' % (time, length)

    def update(self):
        pass

    def handle_event(self, event):
        self.prev_button.handle_event(event)
        self.play_button.handle_event(event)
        self.next_button.handle_event(event)


###############################################################################
# Whirling
###############################################################################

class Whirling(object):
    def __init__(self, displayw, displayh):

        pg.init()

        self.window = pg.display.set_mode((displayw, displayh))
        self.stopped = False
        self.dw = displayw
        self.dh = displayh
        self.font = pg.font.Font(None, 30)
        self.clock = pg.time.Clock()
        self.is_playing = False

        # Create audio controller.
        rect = pg.Rect(0, self.dh*.9, self.dw, self.dh*.1)
        self.audio_controller = AudioController(rect, MUSIC_TRACKS)
        self.Main()

    def Main(self):

        while self.stopped is False:

            # Event Handling.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    self.handle_key_down(event)

                self.audio_controller.handle_event(event)

            # Update
            self.audio_controller.update()

            # Draw
            self.window.fill((0, 0, 0))
            self.render_fps()
            self.render_controls()

            # Update display and clock last.
            pg.display.update()
            self.clock.tick(60)

        # TODO: reset variables here.

    def handle_key_down(self, event):
        if event.key == pg.K_ESCAPE:
            self.stopped = True

    def render_fps(self):
        fps = self.font.render(str(int(self.clock.get_fps())), True, pg.Color('white'))
        self.window.blit(fps, (50, 50))

    def render_controls(self):
        self.audio_controller.draw(self.window)


if __name__ == '__main__':
    display_width = 1280
    display_height = 960
    Whirling(display_width, display_height)
