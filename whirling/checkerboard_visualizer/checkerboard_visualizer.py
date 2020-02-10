import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController


class CheckerboardVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        self.pnts_x = 64
        self.pnts_y = 64
        self.initialize_shader()
        self.create_vbo_data()

    def create_vbo_data(self):
        sw = self.width / self.pnts_x
        sh = self.height / self.pnts_y
        swl = 0.05 * sw
        swr = 0.95 * sw
        shl = 0.05 * sh
        shr = 0.95 * sh

        # Define plot parameters.
        rectangle = []
        indices = []
        count = 0

        # Generate rects and indices for triangles in rect.
        for i in range(self.pnts_x):
            for j in range(self.pnts_y):
                x = i * sw
                y = j * sh
                x1 = round(self.rect.left   + x + swl)
                x2 = round(self.rect.left   + x + swr)
                y1 = round(self.rect.bottom + y + shl)
                y2 = round(self.rect.bottom + y + shr)

                # Add 2 triangles to create a rect.
                rectangle.extend(
                    [
                        # Position      # Color
                        x1, y1, 0.0,   1, 0.0, 1,
                        x2, y1, 0.0,   1, 0.0, 1,
                        x2, y2, 0.0,   1, 0.0, 1,
                        x1, y2, 0.0,   1, 0.0, 1,
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
        self.rectangle = np.array(rectangle, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)

    def initialize_shader(self):
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
        self.shader = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )

    def draw(self):
        super().draw()

        # Create Buffer object in gpu.
        VBO = glGenBuffers(1)

        # Create EBO.
        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        # Bind the buffer.
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(self.rectangle), self.rectangle, GL_STATIC_DRAW)

        # Get the position from shader.
        position = glGetAttribLocation(self.shader, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT,
                              GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Get the color from shader.
        color = glGetAttribLocation(self.shader, 'color')
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE,
                              24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Draw rectangles.
        glUseProgram(self.shader)
        glLoadIdentity()
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT,  None)
        glUseProgram(0)

        glDeleteBuffers(1, [VBO])
        glDeleteBuffers(1, [EBO])
