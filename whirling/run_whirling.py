import os
import json
import logging
import argparse
import coloredlogs
import pygame as pg
from rx.subject.behaviorsubject import BehaviorSubject
from whirling.audio_controller import AudioController
from whirling.audio_visualizer import AudioVisualizer
from whirling import audio_features
from data.tracks import MUSIC_TRACKS

DESIRED_FPS = 45


###############################################################################
# Whirling
###############################################################################

class Whirling(object):
    def __init__(self, plan, displayw, displayh, use_cache=False):

        pg.init()

        self.window = pg.display.set_mode((displayw, displayh))
        pg.display.set_caption('Whirling')
        self.stopped = False
        self.dw = displayw
        self.dh = displayh
        self.font = pg.font.Font(None, 30)
        self.clock = pg.time.Clock()
        self.is_playing = False
        self.current_track = BehaviorSubject('')

        # Generate audio features.
        audio_features.generate_features(plan, MUSIC_TRACKS, use_cache)

        # Create audio controller.
        ac_rect = pg.Rect(0, self.dh*.9, self.dw, self.dh*.1)
        self.audio_controller = AudioController(
            ac_rect, MUSIC_TRACKS, self.current_track)

        # Create audio visualizer.
        v_rect = pg.Rect(0, 0, self.dw, self.dh*.9)
        self.visualizer = AudioVisualizer(v_rect, self.audio_controller,
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
            self.clock.tick(DESIRED_FPS)

    def handle_key_down(self, event):
        if event.key == pg.K_ESCAPE:
            self.stopped = True
        if event.key == pg.K_SPACE:
            self.audio_controller.toggle_play()

    def render_fps(self):
        fps = self.font.render(str(int(self.clock.get_fps())), True, pg.Color('white'))
        self.window.blit(fps, (50, 20))

    def draw(self):
        self.window.fill((0, 0, 0))
        self.visualizer.draw(self.window)
        self.render_fps()
        self.audio_controller.draw(self.window)

###############################################################################
# Main and option handling.
###############################################################################

def load_plan(plan_name):
    full_plan_loc = 'plans/{}.json'.format(plan_name)
    if not os.path.exists(full_plan_loc):
        logging.error('Couldn\'t find plan %s', full_plan_loc)
        quit()
    with open(full_plan_loc, 'r') as f:
        return json.load(f)

def parse_options():
    description = 'A python music visualizer using audio feature extraction'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--plan', type=load_plan, default='default_plan',
         help='A plan to generate data from a list of songs.')
    parser.add_argument('--use-cache', default=False, action='store_true',
         help='Load cached audio features stored as dnz files along side the '
              'original audio file.')
    parser.add_argument('--move-window', default=False, action='store_true',
         help='Moves window to my preferred location')
    parser.add_argument('--move-window2', default=False, action='store_true',
         help='Moves window to my second preferred location')
    args = parser.parse_args()
    return args

def main():
    coloredlogs.install()
    display_width = 1440
    display_height = 1050

    args = parse_options()

    if args.move_window:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1200, 1300)

    if args.move_window2:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 800)

    Whirling(args.plan, display_width, display_height,
             use_cache=args.use_cache)
