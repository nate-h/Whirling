"""Whirling
An individual spectrogram to be rendered by the spectrogram visualizer.
"""

from enum import Enum
import numpy as np
from OpenGL.GL import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLU import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLUT import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
import OpenGL.GL.shaders
from whirling.ui_core.ui_core import UIElement
from whirling.ui_core import viridis


class SpecState(Enum):
    LOADING = 0
    LOADED = 1


class Spectrogram(UIElement):
    def __init__(self, rect, log_db_s, **kwargs):

        super().__init__(rect=rect, **kwargs)

        # A nice way to keep track of loading state.
        self.state = SpecState.LOADING

        self.log_db_s = log_db_s
        self.pnts_x, self.pnts_y = self.log_db_s.shape

        self.create_vbo_data()
        self.shader = self.initialize_shader()

        self.state = SpecState.LOADED

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def draw(self):
        # Create Buffer object in gpu.
        VBO = glGenBuffers(1)
        CBO = glGenBuffers(1)

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
                              GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Bind the buffer.
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
        glDeleteBuffers(1, [VBO])
        glDeleteBuffers(1, [EBO])

    def create_vbo_data(self):
        sw = self.width / self.pnts_x
        sh = self.height / self.pnts_y

        # Generate rectangles and indices for triangles.
        xs = np.linspace(self.rect.left, self.rect.right, num=self.pnts_x, endpoint=False, dtype=np.float32)
        ys = np.linspace(self.rect.bottom, self.rect.top, num=self.pnts_y, endpoint=False, dtype=np.float32)
        x1, y1 = np.meshgrid(xs, ys, sparse=False, indexing='ij')
        zero = np.zeros(x1.shape, dtype=x1.dtype)
        x2 = x1 + sw
        y2 = y1 + sh
        self.rectangle = np.dstack((x1, y1, zero, x2, y1, zero, x2, y2, zero, x1, y2, zero)).flatten()

        # Normalize data for color calculation.
        self.log_db_s = np.clip(self.log_db_s, a_min=-80, a_max=0)
        cmap_ready_s = ((self.log_db_s + 80)/80*99).astype(int).flatten()

        # Convert log_db_s into colorful image.
        grid_colors = viridis.viridis[tuple(cmap_ready_s), :]
        self.grid_colors = np.repeat(grid_colors, 4, axis=0).flatten()

        # Generate triangle indices.
        a = 4* np.arange(0, self.pnts_x * self.pnts_y, dtype=np.uint32)
        b = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        self.indices = (a[:, np.newaxis] + b).flatten()

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
        return OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )
