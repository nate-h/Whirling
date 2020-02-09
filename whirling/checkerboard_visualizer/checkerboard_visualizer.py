import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling.ui_visualizer_base import UIVisualizerBase


FPS_TARGET = 65

class CheckerboardVisualizer(UIVisualizerBase):
    def __init__(self, rect, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, **kwargs)

    def draw(self):
        h = self.height
        w = self.width

        # Define plot parameters.
        pnts_x = 1
        pnts_y = 1
        sw = 2/80
        sh = 2/80
        s = 2/80
        rectangle = []
        indices = []
        count = 0

        # Generate rects and indices for triangles in rect.
        for i in range(pnts_x):
            for j in range(pnts_y):
                x = i * s - 1
                y = j * s - 1
                x1 = x
                x2 = x+s*0.9
                y1 = y
                y2 = y+s*0.9

                # Add 2 triangles to create a rect.
                rectangle.extend(
                    [
                        # Position      # Color
                        self.rect.left, self.rect.top, 0.0,       1, 0.0, 1,
                        self.rect.right, self.rect.top, 0.0,      1, 0.0, 1,
                        self.rect.right, self.rect.bottom, 0.0,   1, 0.0, 1,
                        self.rect.left, self.rect.bottom, 0.0,    1, 0.0, 1,
                    ]
                )

                # Add 3 indexes for each triangle.
                indices.extend(
                    [
                        0 + 4*count, 1 + 4*count, 2 + 4*count,
                        2 + 4*count, 3 + 4*count, 0 + 4*count
                    ]
                )
                count += 1

        # Convert to 32bit float.
        rectangle = np.array(rectangle, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        VERTEX_SHADER = """

            #version 130

            in vec3 position;
            in vec3 color;
            out vec3 newColor;

            void main() {

                gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1.0);
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

        # Compile The Program and shaders.
        shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )

        # Create Buffer object in gpu.
        VBO = glGenBuffers(1)

        # Create EBO.
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

        # Bind the buffer.
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(rectangle), rectangle, GL_STATIC_DRAW)

        # Get the position from shader.
        position = glGetAttribLocation(shader, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT,
                              GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Get the color from shader.
        color = glGetAttribLocation(shader, 'color')
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Draw rectangles.
        glUseProgram(shader)
        glLoadIdentity()
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT,  None)
        glUseProgram(0)
