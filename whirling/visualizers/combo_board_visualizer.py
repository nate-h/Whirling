"""Whirling
Renders a colorful checkerboard.
Just like the checkerboard visualizer but a little more intelligent at
filtering data so the user isn't bombarded with colors.
"""

import math
import random
import colorsys
from OpenGL.GL import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLU import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLUT import * # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
import OpenGL.GL.shaders
import numpy as np
from whirling.visualizers.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController


SETTINGS = {
    'spleeter_vocals': {
        'use': True, 'filter_bins': 12, 'high_pass': 0.25,
        'max_cutoff': 0.75, 'hsl_color': np.array([1/3, 0.5, 1])
    },
    'spleeter_other':  {
        'use': True, 'filter_bins': 12, 'high_pass': 0.25,
        'max_cutoff': 0.73, 'hsl_color': np.array([2/3, 0.5, 1])
    },
    'spleeter_drums':  {
        'use': True, 'filter_bins': 2, 'high_pass': 0.13,
        'max_cutoff': 0.5, 'hsl_color': np.array([0, 0.22, 0.59])
    },
    'spleeter_bass':   {
        'use': True, 'filter_bins': 10, 'high_pass': 0.15,
        'max_cutoff': 0.6, 'hsl_color': np.array([.81, .22, .4])
    },
}


class ComboBoardVisualizer(UIVisualizerBase):
    """Renders a colorful checkerboard.
    Just like the checkerboard visualizer but a little more intelligent at
    filtering data so the user isn't bombarded with colors.
    As of now, it just uses the aggregated track loudness feature but I explored
    using several other features including spectral centroid to jiggle the
    rects. I left that code in but it's not active since I couldn't make it look
    nice.
    """
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        # Create 15 element weighted array.
        self.weights = np.arange(1, 13, dtype=np.float32)

        self.pnts_x = 12
        self.pnts_y = 7
        self.freq_bands = self.pnts_x * self.pnts_y
        self.grid_gap = self.width / 100
        self.initialize_shader()

        self.spec_slices = None
        self.loudness_max = None
        self.loudness_80 = None

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

    def post_process_data(self):
        loudness_smoothed = self.data['full']['features']['loudness_smoothed']
        self.loudness_max = np.max(loudness_smoothed)
        self.loudness_80 = np.percentile(loudness_smoothed, 80)
        self.loudness_20 = np.percentile(loudness_smoothed, 20)

    def loudness_to_saturation_scalar(self, loudness):
        return min(0.25 + 0.81 * math.sqrt(loudness), 1)

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
            used_signals = [s for s in self.data.keys() if s in SETTINGS]
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
        used_signals = [s for s in self.data.keys() if s in SETTINGS]
        current_vals = np.zeros((len(used_signals), self.freq_bands), dtype=np.float32)
        signal_colors = []

        # Calculate colors for signal at current time.
        for i, signal_name in enumerate(used_signals):

            s_obj = self.data[signal_name]

            if signal_name not in SETTINGS:
                continue

            if not SETTINGS[signal_name]['use']:
                continue

            # Get spectrogram data for current time.
            log_db_s = s_obj['spectrograms']['custom_log_db']
            log_db_s_clip = log_db_s[min_window_frame, 0: self.freq_bands]
            log_db_s_clip = (log_db_s_clip + 80) / 80

            # Apply a high pass.
            high_pass = SETTINGS[signal_name]['high_pass']
            log_db_s_clip = (log_db_s_clip - high_pass) /(1 - high_pass)
            log_db_s_clip[log_db_s_clip < 0] = 0

            # Floor everything below max*threshold
            max_cutoff = SETTINGS[signal_name]['max_cutoff']
            localMax = np.max(log_db_s_clip)
            log_db_s_clip[log_db_s_clip < max_cutoff * localMax] = 0

            # Apply moving average.
            # Save up to 'filter_bins' and use that for the average.
            bins = SETTINGS[signal_name]['filter_bins']
            self.spec_slices[signal_name] = np.append(
                self.spec_slices[signal_name], np.array([log_db_s_clip]), axis=0)
            if len(self.spec_slices[signal_name]) > bins:
                self.spec_slices[signal_name] = self.spec_slices[signal_name][-bins:]

            # Calculate final set of values for this signal at time t.
            sig = np.average(self.spec_slices[signal_name], axis=0, weights= \
                             self.weights[:len(self.spec_slices[signal_name])])
            current_vals[i] = sig
            signal_colors.append(np.copy(SETTINGS[signal_name]['hsl_color']))

        # Find brightest signal per frequency and record which signal it was.
        self.max_signal_vals = np.max(current_vals, axis=0)
        which_color_to_use = np.argmax(current_vals, axis=0)

        # Arbitrary effect to make brighter colors pop.
        self.max_signal_vals = self.max_signal_vals ** 1.4 * 1.5
        self.max_signal_vals[self.max_signal_vals > 1] = 1

        # Find loudness value.
        curr_time = self.audio_controller.get_time()
        curr_window_frame = self.get_frame_number(curr_time)
        loudness_smoothed = self.data['full']['features']['loudness_smoothed']
        curr_loudness = loudness_smoothed[curr_window_frame]

        # Adjust saturation.
        saturation_scalar = self.loudness_to_saturation_scalar(curr_loudness)
        for sc in signal_colors:
            sc[2] *= saturation_scalar

        # Convert hsl colors back to rgb.
        signal_colors = [np.array(colorsys.hls_to_rgb(*c)) for c in signal_colors]

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
