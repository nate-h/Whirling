import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np


FPS_TARGET = 65


def debug_print(rectangle, indices, count):
    print('................rectangle')
    for i in np.split(rectangle, len(rectangle)/6):
        print(i)

    print('......... indices')
    for i in np.split(indices, len(indices)/3):
        print(i)
    print('.........')
    print(count)


def main():

    # initialize pygame and setup an opengl display
    pg.init()
    display_width = 1920
    display_height = 1500
    pg.display.set_mode((display_width, display_height), pg.OPENGL|pg.DOUBLEBUF)

    # set opengl to 2d scene
    glDisable(GL_DEPTH_TEST)    # disable our zbuffer
    glDisable(GL_BLEND)
    glMatrixMode(GL_PROJECTION)
    #glLoadIdentity()
    #glOrtho(-10, 110, -10, 70, -1, 1)
    #glLoadIdentity()
    glViewport (0, 0, 100, 60)


    # rectangle = [
    #     # Positions         #Colors
    #     -0.5, -0.5, 0.0,    1.0, 0.0, 0.0,
    #     0.5, -0.5, 0.0,     0.0, 1.0, 0.0,
    #     0.5, 0.5, 0.0,      0.0, 0.0, 1.0,
    #     -0.5, 0.5, 0.0,      1.0, 1.0, 1.0
    # ]

    # Creating Indices
    # indices = [
    #     0, 1, 2,
    #     2, 3, 0
    # ]

    w = 100
    h = 70
    pnts_x = 1
    pnts_y = 1
    s = 1/2.0
    rectangle = []
    indices = []
    count = 0

    for i in range(pnts_x):
        for j in range(pnts_y):
            x = i/pnts_x * w
            y = j/pnts_y * h
            x1 = x-s
            x2 = x+s
            y1 = y-s
            y2 = y+s

            # color fn: y/60.0, 0, x/100.0

            rectangle.extend(
                [
                    x1, y1, 0.0,    1.0, 1.0, 1.0,
                    x2, y1, 0.0,    1.0, 1.0, 1.0,
                    x2, y2, 0.0,    1.0, 1.0, 1.0,
                    x1, y2, 0.0,    1.0, 1.0, 1.0,
                ]
            )
            indices.extend(
                [
                    0 + 4*count, 1 + 4*count, 2 + 4*count,
                    2 + 4*count, 3 + 4*count, 0 + 4*count
                ]
            )
            count += 1

    # convert to 32bit float
    rectangle = np.array(rectangle, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    # Debug print everything.
    debug_print(rectangle, indices, count)

    VERTEX_SHADER = """

        #version 130

        in vec3 position;
        in vec3 color;
        out vec3 newColor;

        void main() {

         gl_Position = vec4(position, 1.0);
         newColor = color;

          }


    """

    FRAGMENT_SHADER = """
        #version 130

        in vec3 newColor;
        out vec4 outColor;

        void main() {

          outColor = vec4(newColor, 1.0f);

        }

    """

    # Compile The Program and shaders
    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    # Create Buffer object in gpu
    VBO = glGenBuffers(1)

    # Create EBO
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

    # Bind the buffer
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, 24*count*4, rectangle, GL_STATIC_DRAW)

    # get the position from shader
    position = glGetAttribLocation(shader, 'position')
    glVertexAttribPointer(position, 3, GL_FLOAT,
                          GL_FALSE, 24*count, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)

    # get the color from shader
    color = glGetAttribLocation(shader, 'color')
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE,
                          24*count, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    glUseProgram(shader)

    clock = pg.time.Clock()
    count = 0

    while True:
        # Check for quit'n events
        event = pg.event.poll()
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            break

        glClear(GL_COLOR_BUFFER_BIT)

        # Draw Triangle
        glDrawElements(GL_TRIANGLES, 6*count, GL_UNSIGNED_INT,  None)

        count += 1
        if count % 100 == 0:
            print(clock.get_fps())

        pg.display.flip()
        clock.tick(FPS_TARGET)



if __name__ == "__main__":
    main()
