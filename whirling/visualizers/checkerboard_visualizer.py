import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling.ui_core.primitives import Point
from whirling.visualizers.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from whirling.tools.code_timer import CodeTimer


class CheckerboardVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        self.freq_bands = 87
        self.pnts_x = 2 * self.freq_bands + 1
        self.pnts_y = 2 * self.freq_bands + 1
        self.initialize_shader()
        self.create_cells()
        self.create_vbo()

    def __del__(self):
        glDeleteBuffers(1, [self.VBO])
        glDeleteBuffers(1, [self.EBO])

    def create_vbo(self):
        # Create Buffer object in gpu.
        self.VBO = glGenBuffers(1)

        # Create EBO.
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        # Bind the buffer.
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(self.rectangle), self.rectangle, GL_STATIC_DRAW)

        # Get the position from shader.
        position = glGetAttribLocation(self.shader, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT,
                              GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

    def draw_visuals(self):

        with CodeTimer('draw_visuals'):
            self.create_grid_colors()

            # Bind the buffer.
            CBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, CBO)
            glBufferData(GL_ARRAY_BUFFER, 4*len(self.grid_colors), self.grid_colors, GL_STATIC_DRAW)

            # Get the color from shader.
            color = glGetAttribLocation(self.shader, 'color')
            glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE,
                                12, ctypes.c_void_p(0))
            glEnableVertexAttribArray(color)

            # Draw rectangles.
            glUseProgram(self.shader)
            glLoadIdentity()
            glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
            glUseProgram(0)

            glDeleteBuffers(1, [CBO])

    def create_cells(self):
        sw = self.width / self.pnts_x
        sh = self.height / self.pnts_y

        # Generate checkerboard vertices.
        xs = np.linspace(self.rect.left, self.rect.right, num=self.pnts_x, endpoint=False, dtype=np.float32)
        ys = np.linspace(self.rect.bottom, self.rect.top, num=self.pnts_y, endpoint=False, dtype=np.float32)
        x1, y1 = np.meshgrid(xs, ys, sparse=False, indexing='ij')
        zero = np.zeros(x1.shape, dtype=x1.dtype)
        x2 = x1 + sw
        y2 = y1 + sh
        self.rectangle = np.dstack((x1, y1, zero, x2, y1, zero, x2, y2, zero, x1, y2, zero)).flatten()

        # Generate triangle indices.
        a = 4* np.arange(0, self.pnts_x * self.pnts_y, dtype=np.uint32)
        b = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        self.indices = (a[:, np.newaxis] + b).flatten()

    def create_grid_colors(self):
        # Generate cell colors.
        r = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)
        g = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)
        b = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)

        grid_colors = np.dstack((r, g, b))

        pnt = self.center_point()

        for i in range(self.freq_bands + 1):
            color = [1, 1, 1]
            side = 2 * i + 1
            self.draw_rect_into_grid(grid_colors, pnt, width=side, height=side, color=color)

        # Repeat color 4 times, one for each cell vertex.
        self.grid_colors = np.repeat(grid_colors.flatten(), 4, axis=0).flatten()

    def center_point(self):
        return Point(int(self.pnts_y/2), int(self.pnts_x/2))

    def draw_rect_into_grid(self, grid_colors, pnt: Point, width: int, height: int, color):
        half_w = int(width/2)
        half_h = int(height/2)
        x1 = max(pnt.x - half_w, 0)
        x2 = min(pnt.x + half_w, self.pnts_x - 1)
        y1 = max(pnt.y - half_h, 0)
        y2 = min(pnt.y + half_h, self.pnts_y - 1)

        grid_colors[x1:x2 + 1, y1, :] = 0.9
        grid_colors[x1:x2 + 1, y2, :] = 0.9
        grid_colors[x1, y1:y2 + 1, :] = 0.9
        grid_colors[x2, y1:y2 + 1, :] = 0.9

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
