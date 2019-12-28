import pygame as pg

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


FPS_TARGET = 60


def tick(i):
  # Draw Axis
  axis(i)
  w = 100
  h = 80
  pnts_x = 70
  pnts_y = 55

  # Draw checkerboard.
  glBegin(GL_QUADS)
  for i in range(pnts_x):
    for j in range(pnts_y):
        x = i/pnts_x * w
        y = j/pnts_y * h
        draw_rect((x, y), 1, (y/60.0, 0, x/100.0))  #(center, diameter, color)
  glEnd()


def axis(i):
  glBegin(GL_LINES)

  #x = red
  #y = green
  #z = blue

  glColor3f(1, 0, 0)
  glVertex3fv((0, 0, 0))
  glVertex3fv((1, 0, 0))

  glColor3f(0, 1, 0)
  glVertex3fv((0, 0, 0))
  glVertex3fv((0, 1, 0))

  glColor3f(0, 0, 1)
  glVertex3fv((0, 0, 0))
  glVertex3fv((0, 0, 1))

  glEnd()

def draw_rect(point, size, color):
  glColor3f(*color)
  x,y = point
  s = size/2.0
  glVertex2f(x-s, y-s)                                   # bottom left point
  glVertex2f(x+s, y-s)                           # bottom right point
  glVertex2f(x+s, y+s)                  # top right point
  glVertex2f(x-s, y+s)                          # top left point

def drawText(position, textString):
    font = pg.font.Font (None, 64)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))
    textData = pg.image.tostring(textSurface, "RGBA", True)
    glRasterPos2d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def main():

  #initialize pygame and setup an opengl display
  pg.init()
  display_width = 1920
  display_height = 1500
  pg.display.set_mode((display_width, display_height), pg.OPENGL|pg.DOUBLEBUF)

  # set opengl to 2d scene
  glDisable(GL_DEPTH_TEST)    # disable our zbuffer
  glDisable(GL_BLEND)
  glMatrixMode(GL_PROJECTION)
  glOrtho(0, 100, 0, 80, -1, 1)

  clock = pg.time.Clock()

  for i in range(2**63):

    #check for quit'n events
    event = pg.event.poll()
    if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
      break

    # clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    tick(i)

    fps = str(int(clock.get_fps()))
    drawText((0, 0), fps)

    pg.display.flip()

    clock.tick(FPS_TARGET)


if __name__ == '__main__':
    main()