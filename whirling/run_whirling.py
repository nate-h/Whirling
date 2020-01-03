import os
import json
import logging
import argparse
import coloredlogs
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from rx.subject.behaviorsubject import BehaviorSubject
#from whirling.audio_controller import AudioController
#from whirling.audio_visualizer import AudioVisualizer
from whirling.ui_core import UIText, UIImage, UIAxis
from whirling.ui_textures import WhirlingTextures
from whirling import audio_features
from data.tracks import MUSIC_TRACKS

DESIRED_FPS = 10


###############################################################################
# Whirling
###############################################################################

class Whirling(object):
    def __init__(self, plan, display_w, display_h, use_cache=False):

        # Initialize window and pygame.
        pg.init()
        pg.display.set_mode((display_w, display_h), pg.OPENGL|pg.DOUBLEBUF)
        pg.display.set_caption('Whirling')
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Initialize all whirling textures.
        whirling_textures = WhirlingTextures()

        # UI element testing.
        self.fps = UIText('FPS', (0.02, 0.98, 0), font_size=50)
        self.next = UIImage(whirling_textures, 'next')


        self.stopped = False
        self.dw = display_w
        self.dh = display_h
        self.clock = pg.time.Clock()
        self.is_playing = False
        self.current_track = BehaviorSubject('')

        # Generate audio features.
        audio_features.generate_features(plan, MUSIC_TRACKS, use_cache)

        # Create audio controller.
        # ac_rect = pg.Rect(0, self.dh*.9, self.dw, self.dh*.1)
        # self.audio_controller = AudioController(
        #     ac_rect, MUSIC_TRACKS, self.current_track)

        # Create audio visualizer.
        # v_rect = pg.Rect(0, 0, self.dw, self.dh*.9)
        # self.visualizer = AudioVisualizer(v_rect, self.audio_controller,
        #     self.current_track)
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

                #self.audio_controller.handle_event(event)

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

    def render_fps(self):
        pass

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1, 0, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT)
        UIAxis()
        self.fps.draw()
        self.next.draw((0, 0), width=0.05, height=0.05)
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
