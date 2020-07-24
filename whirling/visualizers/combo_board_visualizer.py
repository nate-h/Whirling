"""
    0. Start off with checkerboard
    1. Local value modifies l
    2. Local value modifies square size
    4. Spectral centroid modifies random jiggle size.
    3. Full volume modifies s
"""

# Get full
# Get spectral centroid

import random
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

from scipy.signal import argrelextrema

settings = {
    'spleeter_vocals': {
        'use': True, 'filter_bins': 8, 'high_pass': 0.20,
        'color': np.array([0.23, 1, .08]), 'max_cutoff': 0.8,
    },
    'spleeter_other':  {
        'use': True, 'filter_bins': 8, 'high_pass': 0.2,
        'color': np.array([.243, 0, 1]), 'max_cutoff': 0.8,
    },
    'spleeter_drums':  {
        'use': True, 'filter_bins': 3, 'high_pass': 0.2,
        'color': np.array([1, 0.0274, 0.2274]), 'max_cutoff': 0.86,
    },
    'spleeter_bass':   {
        'use': True, 'filter_bins': 8, 'high_pass': 0.1,
        'color': np.array([0.54, 0.0, 0.54]), 'max_cutoff': 0.7,
    },
}

class ComboBoardVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        # Create 15 element weighted array.
        base = 1/1.75/5
        self.weights = 5*[base] + 5*[base/2] + 5*[base/4]

        self.pnts_x = 12
        self.pnts_y = 7
        self.freq_bands = self.pnts_x * self.pnts_y
        self.grid_gap = self.width / 100
        self.initialize_shader()

        self.spec_slices = None

        # Setup cell colors.
        r = np.zeros((self.pnts_x, self.pnts_y), dtype=np.float32)
        g = np.zeros((self.pnts_x, self.pnts_y), dtype=np.float32)
        b = np.zeros((self.pnts_x, self.pnts_y), dtype=np.float32)
        self.grid_colors = np.dstack((r, g, b))
        self.grid_colors_flat = None

        # Setup max value array.
        self.max_signal_vals = np.zeros((self.freq_bands), dtype=np.float32)

    def __del__(self):
        pass

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

        if not self.spec_slices:
            self.spec_slices = {}
            used_signals = [s for s in self.data.keys() if s in settings]
            for signal_name in used_signals:
                self.spec_slices[signal_name] = np.empty((0, self.freq_bands), dtype=np.float32)

        self.create_grid_colors()
        self.create_cells()
        self.create_vbo()

        # TODO don't attach vbo/ebo to self.

        # Bind the buffer.
        CBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, CBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(self.grid_colors_flat), self.grid_colors_flat, GL_STATIC_DRAW)

        # Get the color from shader.
        color = glGetAttribLocation(self.shader, 'color')
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(color)

        # Draw rectangles.
        glUseProgram(self.shader)
        glLoadIdentity()
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glUseProgram(0)

        glDeleteBuffers(1, [self.EBO])
        glDeleteBuffers(1, [self.VBO])
        glDeleteBuffers(1, [CBO])

    def create_cells(self):
        sw = (self.width - (self.pnts_x - 1) * self.grid_gap) / self.pnts_x
        sh = (self.height - (self.pnts_y - 1) * self.grid_gap) / self.pnts_y

        # Calculate changing square size.
        # DISABLED FOR NOW. IT DOESN'T LOOK GOOD.
        # vals = self.calculate_square_deltas()
        vals = np.zeros((self.pnts_x, self.pnts_y), dtype=np.float32)
        vals_x = vals * sw
        vals_y = vals * sh

        # Generate checkerboard vertices.
        xs = np.linspace(self.rect.left, self.rect.right + self.grid_gap,
            num=self.pnts_x, endpoint=False, dtype=np.float32)
        ys = np.linspace(self.rect.bottom, self.rect.top + self.grid_gap,
            num=self.pnts_y, endpoint=False, dtype=np.float32)
        x1, y1 = np.meshgrid(xs, ys, sparse=False, indexing='ij')
        zero = np.zeros(x1.shape, dtype=x1.dtype)
        x2 = x1 + sw
        y2 = y1 + sh

        # Adjust square size based on frequency intensity.
        x1 = x1 + vals_x
        x2 = x2 - vals_x
        y1 = y1 + vals_y
        y2 = y2 - vals_y

        self.rectangle = np.dstack((x1, y1, zero, x2, y1, zero, x2, y2, zero, x1, y2, zero)).flatten()

        # Generate triangle indices.
        a = 4* np.arange(0, self.pnts_x * self.pnts_y, dtype=np.uint32)
        b = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        self.indices = (a[:, np.newaxis] + b).flatten()

    def calculate_square_deltas(self):
        # Calculate each square size based on it's frequency intensity.
        max_vals_shaped = self.max_signal_vals[:].reshape(self.pnts_x, self.pnts_y)
        max_vals_shaped *= 2  # Make values closer to 1.
        max_vals_shaped[max_vals_shaped > 1] = 1  # Cap at 1.
        max_contraction = 0.25
        vals = (1 - max_vals_shaped) / 2 * max_contraction
        return vals

    def jiggle_squares(self):
        # Get current spectral centroid.
        curr_time = self.audio_controller.get_time()
        curr_window_frame = self.get_frame_number(curr_time)
        spec_centroid_data = self.data['full']['features']['spectral_centroid']
        curr_spec_centroid = spec_centroid_data[curr_window_frame]

        # Calculate jiggle values.
        jiggle_aggressiveness = 0.01
        self.jiggle_x = self.jiggle_x * 0.99
        self.jiggle_x[self.jiggle_x < -1] = -1
        self.jiggle_x[self.jiggle_x > 1] = 1
        rand_x = random.uniform(-1, 1)
        jiggle_delta_x = rand_x * jiggle_aggressiveness * curr_spec_centroid
        self.jiggle_x += jiggle_delta_x

    def create_grid_colors(self):

        # Reset colors.
        self.grid_colors[:] = 0

        curr_time = self.audio_controller.get_time()
        min_window_frame = self.get_frame_number(curr_time)
        used_signals = [s for s in self.data.keys() if s in settings]
        current_vals = np.zeros((len(used_signals), self.freq_bands), dtype=np.float32)
        signal_colors = []

        # Calculate colors for signal at current time.
        for i, signal_name in enumerate(used_signals):

            s_obj = self.data[signal_name]

            if signal_name not in settings:
                continue

            if not settings[signal_name]['use']:
                continue

            # Get spectrogram data for current time.
            log_db_s = s_obj['spectrograms']['custom_log_db']
            log_db_s_clip = log_db_s[min_window_frame, 0: self.freq_bands]
            log_db_s_clip = (log_db_s_clip + 80) / 80

            # Apply a high pass.
            high_pass = settings[signal_name]['high_pass']
            log_db_s_clip = (log_db_s_clip - high_pass) /(1 - high_pass)
            log_db_s_clip[log_db_s_clip < 0] = 0

            # Floor everything below max*threshold
            max_cutoff = settings[signal_name]['max_cutoff']
            localMax = np.max(log_db_s_clip)
            log_db_s_clip[log_db_s_clip < max_cutoff * localMax] = 0

            # Apply moving average.
            # Save up to 'filter_bins' and use that for the average.
            bins = settings[signal_name]['filter_bins']
            self.spec_slices[signal_name] = np.append(
                self.spec_slices[signal_name], np.array([log_db_s_clip]), axis=0)
            if len(self.spec_slices[signal_name]) > bins:
                self.spec_slices[signal_name] = self.spec_slices[signal_name][-bins:]

            # Calculate final set of values for this signal at time t.
            sig = np.average(self.spec_slices[signal_name], axis=0)
            current_vals[i] = sig
            #weights=self.weights[:len(self.spec_slices[signal_name])])
            signal_colors.append(settings[signal_name]['color'])

        # Find brightest signal per frequency and record which signal it was.
        self.max_signal_vals = np.max(current_vals, axis=0)
        which_color_to_use = np.argmax(current_vals, axis=0)

        # Arbitrary effect to make brighter colors pop.
        self.max_signal_vals = self.max_signal_vals ** 1.4 * 1.5
        self.max_signal_vals[self.max_signal_vals > 1] = 1

        # Render colors.
        for i, val in enumerate(self.max_signal_vals):
            color = signal_colors[which_color_to_use[i]] * val
            self.draw_rect_into_grid(self.grid_colors, color=color, index=i)

        # Repeat color 4 times, one for each cell vertex.
        self.grid_colors_flat = np.repeat(self.grid_colors.reshape(-1, self.grid_colors.shape[-1]), 4, axis=0).flatten()

    def draw_rect_into_grid(self, grid_colors, color, index: int):
        x = index % self.pnts_x
        y = int(index / self.pnts_x)
        grid_colors[x, y, :] += color

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
