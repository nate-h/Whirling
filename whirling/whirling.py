import pygame as pg
from rx.subject.behaviorsubject import BehaviorSubject
import whirling_ui as UI
from whirling_audio_controller import WhirlingAudioController
from whirling_visualizer import WhirlingVisualizer

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
        self.current_track = BehaviorSubject('')

        # Create audio controller.
        ac_rect = pg.Rect(0, self.dh*.9, self.dw, self.dh*.1)
        v_rect = pg.Rect(0, 0, self.dw, self.dh*.9)
        self.audio_controller = WhirlingAudioController(
            ac_rect, MUSIC_TRACKS, self.current_track)
        self.visualizer = WhirlingVisualizer(v_rect,
                                             self.audio_controller,
                                             self.current_track)
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

            # Draw visuals
            self.draw()

            # Update display and clock last.
            pg.display.update()
            self.clock.tick(60)

    def handle_key_down(self, event):
        if event.key == pg.K_ESCAPE:
            self.stopped = True

    def render_fps(self):
        fps = self.font.render(str(int(self.clock.get_fps())), True, pg.Color('white'))
        self.window.blit(fps, (50, 50))

    def draw(self):
        self.window.fill((0, 0, 0))
        self.visualizer.draw(self.window)
        self.render_fps()
        self.audio_controller.draw(self.window)


if __name__ == '__main__':
    display_width = 1280
    display_height = 960
    Whirling(display_width, display_height)
