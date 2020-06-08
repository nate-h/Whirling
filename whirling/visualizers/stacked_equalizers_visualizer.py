from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling.ui_core import colors
from whirling.ui_core.primitives import Point
from whirling.visualizers.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from whirling.tools.code_timer import CodeTimer

settings = {
    'librosa_harmonic':   {
        'use': False, 'filter_bins': 30, 'high_pass': 0.5,
        'color': np.array([0, 1, 0]), 'order': 1
    },
    'librosa_percussive': {
        'use': False, 'filter_bins': 3, 'high_pass': 0.5,
        'color': np.array([1, 0, 0]), 'order': 1
    },

    'spleeter_vocals': {
        'use': True, 'filter_bins': 12, 'high_pass': 0.1,
        'color': np.array([0.23, 1, .08]), 'order': 2
    },
    'spleeter_other':  {
        'use': True, 'filter_bins': 10, 'high_pass': 0.1,
        'color': np.array([.243, 0, 1]), 'order': 1
    },
    'spleeter_drums':  {
        'use': True, 'filter_bins': 3, 'high_pass': 0.1,
        'color': np.array([1, 0, 0]), 'order': 3
    },
    'spleeter_bass':   {
        'use': True, 'filter_bins': 10, 'high_pass': 0.1,
        'color': np.array([0.54, 0.0, 0.54]), 'order': 0
    },
}

class StackedEqualizersVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        self.freq_bands = 81
        self.initialize_shader()
        self.stems = len([k for k in self.data if settings[k]['use']])
        self.rectangle = None

        # Create a sorted list of stems, colors, order. Where order corresponds
        # to the order each stem appears in a stacked bar.
        self.color_order = \
            sorted([
                [k, v['color'], v['order']] for k, v in settings.items()
                if k in self.data.keys() and v['use']
            ], key=lambda x: x[2])

        # Create an array to represent the colors the bar chart will have.
        self.create_cbo_and_ebo()

        self.spec_slices = {}
        for signal_name in self.data:
            self.spec_slices[signal_name] = np.empty((0, self.freq_bands), dtype=np.float32)


    def __del__(self):
        glDeleteBuffers(1, [self.CBO])
        glDeleteBuffers(1, [self.EBO])

    def draw_visuals(self):

        self.create_vbo()

        # Draw rectangles.
        glUseProgram(self.shader)
        glLoadIdentity()
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glUseProgram(0)

        glDeleteBuffers(1, [self.VBO])

    def create_cbo_and_ebo(self):

        # Create flattened grid of colors.
        ordered_colors = np.array([obj[1] for obj in self.color_order], dtype=np.float32)
        grid_colors_flat = np.repeat(ordered_colors, 4*self.freq_bands, axis=0).flatten()

        # Bind the buffer.
        self.CBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.CBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(grid_colors_flat), grid_colors_flat, GL_STATIC_DRAW)

        # Get the color from shader.
        color = glGetAttribLocation(self.shader, 'color')
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(color)

        # Generate triangle indices.
        a = 4 * np.arange(0, self.freq_bands * self.stems, dtype=np.uint32)
        b = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        self.indices = (a[:, np.newaxis] + b).flatten()

        # Create EBO.
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

    def create_vbo(self):

         # Settings.
        sw = self.width / self.freq_bands
        sh = self.height / self.stems

        curr_time = self.audio_controller.get_time()
        min_window_frame = self.get_frame_number(curr_time)

        x0 = np.linspace(self.rect.left, self.rect.right, num=self.freq_bands, endpoint=False, dtype=np.float32)
        x_left = np.tile(x0, (self.stems, 1))
        x_right = x_left + sw

        zero = np.zeros(x_left.shape, dtype=x_left.dtype)

        y_lower = np.zeros(x_left.shape, dtype=x0.dtype)
        y_upper = np.zeros(x_left.shape, dtype=x0.dtype)

        # Set first row of y lower.
        y0 = np.zeros(x0.shape, dtype=x0.dtype)
        y_lower[0, :] = y0

        y_previous = y0


        count = 0
        for s_array in self.color_order:  # Is this the same order as "color_order"

            signal_name = s_array[0]
            s_obj = self.data[signal_name]

            log_db_s = s_obj['spectrograms']['custom_log_db']
            log_db_s_clip = log_db_s[min_window_frame, 0: self.freq_bands]
            log_db_s_clip = (log_db_s_clip + 80) / 80

            # High pass.
            high_pass = settings[signal_name]['high_pass']
            log_db_s_clip[log_db_s_clip < high_pass] = 0

            # Scale up anything that needs to pop.
            scalar = 1.8
            log_db_s_clip = log_db_s_clip * scalar
            log_db_s_clip[log_db_s_clip > 2] = 2

            # Apply moving average.
            # Save up to 'filter_bins' and use that for the average.
            bins = settings[signal_name]['filter_bins']
            self.spec_slices[signal_name] = np.append(
                self.spec_slices[signal_name], np.array([log_db_s_clip]), axis=0)
            if len(self.spec_slices[signal_name]) > bins:
                self.spec_slices[signal_name] = self.spec_slices[signal_name][-bins:]
            log_db_s_clip = np.average(self.spec_slices[signal_name], axis=0)

            y_current = y_previous + log_db_s_clip*sh

            # Don't add last signal to y lower.
            # Because y_upper didn't get zeroth row.
            if count < self.stems - 1:
                y_lower[count + 1, :] = y_current

            y_upper[count, :] = y_current

            y_previous = y_current
            count += 1

        self.rectangle = np.dstack(
            (x_left, y_lower, zero, x_right, y_lower, zero, x_right, y_upper,
            zero, x_left, y_upper, zero)
        ).flatten()

        # Create Buffer object in gpu.
        self.VBO = glGenBuffers(1)

        # Bind the buffer.
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(self.rectangle), self.rectangle, GL_STATIC_DRAW)

        # Get the position from shader.
        position = glGetAttribLocation(self.shader, 'position')
        glVertexAttribPointer(position, 3, GL_FLOAT,
                              GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

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
