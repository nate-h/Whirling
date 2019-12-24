import time
import pygame as pg

from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from OpenGL.arrays import vbo

import math


###############################################################################
# Action Happens Here 50 times per second

def tick(i):
  #glRotatef(1, 0, 0, 1)
  #glTranslatef(0, 0, 1)

  # Draw Axis
  axis(i)
  w = 100
  h = 70
  pnts_x = 40
  pnts_y = 40

  # Draw sinewave
  for i in range(pnts_x):
    for j in range(pnts_y):
        x = i/pnts_x * w
        y = j/pnts_y * h
        cquad((x, y, 0), 1, (y/60.0, 0, x/100.0))  #(center, diameter, color)

    # for x in range(200):
    #     x = x/2.0
    #     y = math.sin(math.radians(x+i) * 10) * 30 + 30
    #     cquad((x, y, 0), 1, (y/60.0, 0, x/100.0))  #(center, diameter, color)

###############################################################################
# The rest of this is the bones that make it work

FPS_TARGET = 50



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

def quad(points, color):
  glBegin(GL_QUADS)
  glColor3f(*color)
  for p in points:
    glVertex3fv(p)
  glEnd()

def cquad(point, size, color):
  glBegin(GL_QUADS)
  glColor3f(*color)
  x,y,z = point
  s = size/2.0
  glVertex3fv((x-s,y-s,z))
  glVertex3fv((x+s,y-s,z))
  glVertex3fv((x+s,y+s,z))
  glVertex3fv((x-s,y+s,z))
  glEnd()

import OpenGL.GL as ogl
def drawText(position, textString):
    font = pg.font.Font (None, 64)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))
    textData = pg.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def main():

  #initialize pygame and setup an opengl display
  pg.init()
  display_width = 1920
  display_height = 1500
  pg.display.set_mode((display_width, display_height), pg.OPENGL|pg.DOUBLEBUF)
  glDisable(GL_DEPTH_TEST)    # disable our zbuffer

  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  #setup the camera
  glMatrixMode(GL_PROJECTION)
  #gluPerspective(45.0,1000/1000,0.1,1000.0)  #setup lens
  #glOrtho(-10,10,-10,10,1,20)
  glOrtho(-10, 110, -10, 70, -1, 1)

  #glTranslatef(0, 0, -100)        #move back
  #glRotatef(-20, 1, 0, 0)             #orbit higher

  clock = pg.time.Clock()

  for i in range(2**63):

    #check for quit'n events
    event = pg.event.poll()
    if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
      break

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    tick(i)

    fps = str(int(clock.get_fps()))
    drawText((0, 0, 0), fps)

    pg.display.flip()

    clock.tick(FPS_TARGET)


if __name__ == '__main__':
    main()