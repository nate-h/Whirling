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

  # Draw sinewave
  for x in range(200):
    x = x/2.0
    y = math.sin(math.radians(x+i) * 10) * 30 + 30
    cquad((x, y, 0), 1, (y/60.0, 0, x/100.0))  #(center, diameter, color)

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


def main():

  #initialize pygame and setup an opengl display
  pg.init()
  pg.display.set_mode((1200,800), pg.OPENGL|pg.DOUBLEBUF)
  glEnable(GL_DEPTH_TEST)    #use our zbuffer

  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

  #setup the camera
  glMatrixMode(GL_PROJECTION)
  #gluPerspective(45.0,1000/1000,0.1,1000.0)  #setup lens
  #glOrtho(-10,10,-10,10,1,20)
  glOrtho(-10, 110, -10, 70, -1, 1)

  #glTranslatef(0, 0, -100)        #move back
  #glRotatef(-20, 1, 0, 0)             #orbit higher


  nt = int(time.time() * 1000)

  for i in range(2**63):
    nt += 1000//FPS_TARGET

    #check for quit'n events
    event = pg.event.poll()
    if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
      break

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    tick(i)

    pg.display.flip()

    ct = int(time.time() * 1000)
    pg.time.wait(max(1, nt - ct))

    if i % FPS_TARGET == 0:
      print(nt-ct)


if __name__ == '__main__': main()