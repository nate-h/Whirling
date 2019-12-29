from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame as pg
import OpenGL.GL as ogl

count = 0
fonts = [
    'whirling/fonts/Roboto-Black.ttf',
    'whirling/fonts/SourceCodePro-Regular.otf'
]


def ui_text(position, text_string):
    global count
    #font = pg.font.Font(None, 10)
    font = pg.font.Font(fonts[1], 20)
    textSurface = font.render(text_string, True, (255,255,255,255), (0,0,0,255))
    textData = pg.image.tostring(textSurface, "RGBA", True)

    print('text_string:', text_string)
    print(textSurface.get_width())
    print(textSurface.get_height())
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(),
                 GL_RGBA, GL_UNSIGNED_BYTE, textData)
    count += 1

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