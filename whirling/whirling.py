import pygame as pg
import whirling_ui as UI
import whirling_audio_controller as wac

MUSIC_TRACKS = [
    'data/Christian Löffler - Mare/Christian Löffler - Mare - 02 Haul (feat. Mohna).mp3',
    'data/bensound-buddy.mp3'
]


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
        self.audio_controller = wac.WhirlingAudioController(rect, MUSIC_TRACKS)
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
