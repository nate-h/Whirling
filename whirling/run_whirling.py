import os
import json
import logging
import argparse
import coloredlogs
import pygame as pg
from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
import OpenGL.GL.shaders
import numpy as np
from rx.subject.behaviorsubject import BehaviorSubject
from whirling.primitives import Rect
from whirling.audio_controller import AudioController
#from whirling.audio_visualizer import AudioVisualizer
from whirling.ui_core import UIText, UIImage, UIAxis
from whirling.ui_textures import WhirlingTextures
from whirling import audio_features
from data.tracks import MUSIC_TRACKS
from whirling import colors

from whirling.ui_audio_controller import UIAudioController
from whirling.ui_visualizer import UIVisualizer
from whirling.ui_visualizer_controller import UIVisualizerController

DESIRED_FPS = 10


###############################################################################
# Whirling
###############################################################################

class Whirling(object):
    def __init__(self, plan, display_w, display_h, use_cache=False):

        # Initialize window and pygame.
        self.width = display_w
        self.height = display_h

        # Verify window height is much greater than window width.
        if 1.05*display_w > display_h:
            msg = 'Window height needs to greater than 1.05 * window width.\n'\
                'This is so enough space is allocated for the bottom controls.'
            logging.error(msg)
            pg.quit()
            quit()

        # Define rects for main UI elements.
        bottom_controls_h = display_h - display_w
        ac_w = 0.6 * display_w
        visualizer_rect = Rect(0, display_h, display_w, bottom_controls_h)
        audio_controller_rect = Rect(
            0, bottom_controls_h, ac_w, 0)
        visualizer_controller_rect = Rect(
            ac_w, bottom_controls_h, display_w, 0)

        # Initialize pygame and opengl.
        pg.init()
        pg.display.set_mode((display_w, display_h), pg.OPENGL|pg.DOUBLEBUF)
        pg.display.set_caption('Whirling')
        glMatrixMode(GL_PROJECTION)
        glOrtho(0, display_w, 0, display_h, -1, 1)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Initialize audio controller.
        self.is_playing = False
        self.current_track = BehaviorSubject('')
        self.audio_controller = UIAudioController(
            MUSIC_TRACKS, self. current_track, rect=audio_controller_rect,
            bg_color=(0.1,0.1,0.1), border_color=(0.15,0.15,0.15))

        # Initialize visualizer controller.
        self.visualizer_controller = UIVisualizerController(
            rect=visualizer_controller_rect,
            bg_color=(0.1,0.1,0.1), border_color=(0.15,0.15,0.15))

        # Initialize visualizer.
        self.visualizer = UIVisualizer(rect=visualizer_rect)

        # UI element testing.
        offset_x = 0.01 * self.width
        offset_y = self.height - 0.05 * self.width
        self.fps = UIText('FPS', (offset_x, offset_y), font_size=50)

        self.stopped = False
        self.dw = display_w
        self.dh = display_h
        self.clock = pg.time.Clock()

        # Generate audio features.
        audio_features.generate_features(plan, MUSIC_TRACKS, use_cache)

        # Create audio controller.
        # self.audio_controller = AudioController(ac_rect, MUSIC_TRACKS, self.current_track)

        # Create audio visualizer.
        # self.visualizer = AudioVisualizer(v_rect, self.audio_controller, self.current_track)
        self.main_loop()

    def main_loop(self):

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
            #self.audio_controller.update()
            self.fps.text = str(int(self.clock.get_fps()))

            # Draw visuals
            self.draw()

            # Update display and clock last.
            self.clock.tick(DESIRED_FPS)

        # If exit loop, quit pygame.
        pg.quit()
        quit()

    def handle_key_down(self, event):
        if event.key == pg.K_ESCAPE:
            self.stopped = True
        elif event.key == pg.K_SPACE:
            self.audio_controller.toggle_play()
        elif event.key == pg.K_LEFT:
            self.audio_controller.adjust_time_by(-2)
        elif event.key == pg.K_RIGHT:
            self.audio_controller.adjust_time_by(2)

    def draw(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw debug axis.
        # UIAxis(0.9*self.width, .1).draw()

        self.visualizer.draw()
        self.audio_controller.draw()
        self.visualizer_controller.draw()

        self.fps.draw()

        pg.display.flip()

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
    display_width = 1500
    display_height = 1600

    args = parse_options()

    if args.move_window:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1400, 1300)

    if args.move_window2:
        # Position window in lower left corner.
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 800)

    Whirling(args.plan, display_width, display_height,
             use_cache=args.use_cache)
