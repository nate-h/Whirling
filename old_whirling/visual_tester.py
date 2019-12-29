import os
import json
import logging
import argparse
import coloredlogs
import pygame as pg
from rx.subject.behaviorsubject import BehaviorSubject
from whirling.audio_controller import AudioController
from whirling.audio_visualizer import AudioVisualizer
from whirling.checker_board_visual import CheckerBoardVisual
from whirling import audio_features
from data.tracks import MUSIC_TRACKS

DESIRED_FPS = 45


###############################################################################
# Visual Tester.
###############################################################################

class VisualTester(object):
    """ This class is used exclusively to get new visuals working.
    """
    def __init__(self, VisualizerClass, displayw, displayh):

        pg.init()

        self.window = pg.display.set_mode((displayw, displayh))
        pg.display.set_caption('Visualizer Tester')
        self.stopped = False
        self.dw = displayw
        self.dh = displayh
        self.font = pg.font.Font(None, 30)
        self.clock = pg.time.Clock()

        # Initialize visualizer class.
        self.visualizer = VisualizerClass(self.dw, self.dh)

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

            # Handle any events.
            # self.visualizer.handle_event(event)

            # Update.
            self.visualizer.update()

            # Draw visuals.
            self.draw()

            # Update display and clock last.
            pg.display.update()
            self.clock.tick(DESIRED_FPS)

    def handle_key_down(self, event):
        if event.key == pg.K_ESCAPE:
            self.stopped = True
        # elif event.key == pg.K_SPACE:
        #     self.audio_controller.toggle_play()
        # elif event.key == pg.K_LEFT:
        #     self.audio_controller.adjust_time_by(-2)
        # elif event.key == pg.K_RIGHT:
        #     self.audio_controller.adjust_time_by(2)

    def render_fps(self):
        fps = self.font.render(str(int(self.clock.get_fps())), True, pg.Color('white'))
        self.window.blit(fps, (50, 20))

    def draw(self):
        self.window.fill((0, 0, 0))
        self.visualizer.draw(self.window)
        self.render_fps()

###############################################################################
# Main and option handling.
###############################################################################

def parse_options():
    description = 'A python music visualizer using audio feature extraction'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--visualizer', type=get_visualizer_class, default='checker_board',
         help='A plan to generate data from a list of songs.')
    parser.add_argument('--move-window', default=False, action='store_true',
         help='Moves window to my preferred location')
    parser.add_argument('--move-window2', default=False, action='store_true',
         help='Moves window to my second preferred location')
    args = parser.parse_args()
    return args

def get_visualizer_class(visualizer_class):
    classes = {
        'checker_board': CheckerBoardVisual
    }
    if visualizer_class in classes:
        return classes[visualizer_class]
    else:
        logging.error('Couldn\'t find visualizer class %s', visualizer_class)
        quit()

def main():
    coloredlogs.install()
    display_width = 1920
    display_height = 1500

    args = parse_options()

    if args.move_window:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1200, 1300)

    if args.move_window2:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 800)

    VisualTester(args.visualizer, display_width, display_height)
