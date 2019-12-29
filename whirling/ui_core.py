from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame as pg
import OpenGL.GL as ogl
from enum import Enum


class AnchorPositions(Enum):
    BOTTOM_LEFT = 0  # Anchor will be attached at bottom left of text
    TOP_LEFT = 1     # Anchor will be attached at top left of text


class UIElement():
    def __init__(self):
        # declare position
        self.position = (0, 0, 0)
        self.anchor_position = AnchorPositions.TOP_LEFT

    def draw(self):
        pass

    def update(self):
        pass

    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    def translate_position(self, position, anchor_position):
        x = position[0]
        y = position[1]
        z = position[2]
        _window_w, window_h = pg.display.get_surface().get_size()

        # Process anchor.
        if anchor_position == AnchorPositions.TOP_LEFT:
            y -= self.height/window_h

        print(self.height/window_h)

        # return translated position.
        return (x, y, z)


class UIText(UIElement):
    fonts = {
        'roboto' :'whirling/fonts/Roboto-Black.ttf',
        'mono' :'whirling/fonts/SourceCodePro-Regular.otf'
    }
    def __init__(self, text_string, position, font_size=30, font_key='mono',
                 font_color=(255,255,255,255), font_bg=(0,0,0,255),
                 anchor_position=AnchorPositions.TOP_LEFT):
        self.font = pg.font.Font(self.fonts[font_key], font_size)
        self.text = text_string
        self.text_surface = self.font.render(text_string, True, font_color, font_bg)
        self.text_data = pg.image.tostring(self.text_surface, "RGBA", True)
        self.position = self.translate_position(position, anchor_position)

    @property
    def width(self):
        return self.text_surface.get_width()

    @property
    def height(self):
        return self.text_surface.get_height()

    def draw(self):
        print(self.height)
        glRasterPos3d(*self.position)
        glDrawPixels(self.width, self.height,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.text_data)

def axis():
  glBegin(GL_LINES)

  # Red for x.
  glColor3f(1, 0, 0)
  glVertex3fv((0, 0.001, 0))
  glVertex3fv((0.9, 0.001, 0))

  # Green for y.
  glColor3f(0, 1, 0)
  glVertex3fv((0.001, 0, 0))
  glVertex3fv((0.001, 0.9, 0))

  # Blue for z.
  glColor3f(0, 0, 1)
  glVertex3fv((0, 0, 0))
  glVertex3fv((0, 0, 0.9))

  glEnd()