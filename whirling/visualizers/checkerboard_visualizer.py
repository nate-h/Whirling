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
    'librosa_harmonic':   {'use': False, 'filter_bins': 30, 'high_pass': 0.5, 'color': np.array([0, 1, 0]), "keep_biggest":5},
    'librosa_percussive': {'use': False, 'filter_bins': 3, 'high_pass': 0.5, 'color': np.array([1, 0, 0]), "keep_biggest":5},

    'spleeter_vocals': {'use': True, 'filter_bins': 20, 'high_pass': 0.4, 'color': np.array([0.23, 1, .08]), "keep_biggest":5},
    'spleeter_other':  {'use': True, 'filter_bins': 20, 'high_pass': 0.5, 'color': np.array([.243, 0, 1]), "keep_biggest":5},
    'spleeter_drums':  {'use': True, 'filter_bins': 3, 'high_pass': 0.2, 'color': np.array([1, 0, 0]), "keep_biggest":7},
    'spleeter_bass':   {'use': True, 'filter_bins': 5, 'high_pass': 0.3, 'color': np.array([0.54, 0.0, 0.54]), "keep_biggest":3},
}

class CheckerboardVisualizer(UIVisualizerBase):
    def __init__(self, rect, audio_controller: UIAudioController, **kwargs):
        # Initialize base class.
        super().__init__(rect=rect, audio_controller=audio_controller, **kwargs)

        self.freq_bands = 87
        self.pnts_x = 2 * self.freq_bands + 1
        self.pnts_y = 2 * self.freq_bands + 1 # TODO: set dynamically w/ data.
        self.initialize_shader()
        self.create_cells()
        self.create_vbo()

        self.spec_slices = None

        # Generate cell colors.
        r = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)
        g = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)
        b = np.zeros((self.pnts_y, self.pnts_x), dtype=np.float32)
        self.grid_colors = np.dstack((r, g, b))
        self.grid_colors_flat = None

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

        if not self.spec_slices:
            self.spec_slices = {}
            for signal_name in self.data:
                self.spec_slices[signal_name] = np.empty((0, self.freq_bands), dtype=np.float32)

        self.create_grid_colors()

        # Bind the buffer.
        CBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, CBO)
        glBufferData(GL_ARRAY_BUFFER, 4*len(self.grid_colors_flat), self.grid_colors_flat, GL_STATIC_DRAW)

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

        # Settings.
        past_weights = 0.5
        new_weight = 1 - past_weights

        # Subtract a small amount each frame and floor at zero.
        self.grid_colors[:] = self.grid_colors[:] * past_weights
        self.grid_colors[self.grid_colors < 0] = 0
        self.grid_colors[self.grid_colors > 1] = 1

        curr_time = self.audio_controller.get_time()
        min_window_frame = self.get_frame_number(curr_time)
        count = 0

        pnt = self.center_point()

        for signal_name, s_obj in self.data.items():
            if not settings[signal_name]['use']:
                continue

            log_db_s = s_obj['spectrograms']['custom_log_db']
            log_db_s_clip = log_db_s[min_window_frame, 0: self.freq_bands]
            log_db_s_clip = (log_db_s_clip + 80) / 80

            # High pass.
            high_pass = settings[signal_name]['high_pass']
            log_db_s_clip[log_db_s_clip < high_pass] = 0

            # Floor all values smaller than nth largest values.
            keep_biggest = settings[signal_name]['keep_biggest']
            idxs = np.argpartition(log_db_s_clip, -keep_biggest)
            val = log_db_s_clip[idxs[-keep_biggest]]
            log_db_s_clip[log_db_s_clip < val] = 0


            # Apply moving average.
            bins = settings[signal_name]['filter_bins']
            self.spec_slices[signal_name] = np.append(
                self.spec_slices[signal_name], np.array([log_db_s_clip]), axis=0)
            if len(self.spec_slices[signal_name]) > bins:
                self.spec_slices[signal_name] = self.spec_slices[signal_name][-bins:]
            log_db_s_clip = np.average(self.spec_slices[signal_name], axis=0)

            c = settings[signal_name]['color']

            for i, v in enumerate(log_db_s_clip):
                side = 2 * i + 1
                c_i = c * v * new_weight
                self.draw_rect_into_grid(self.grid_colors, pnt, width=side, height=side, color=c_i)

        # Repeat color 4 times, one for each cell vertex.
        self.grid_colors_flat = np.repeat(self.grid_colors.reshape(-1, self.grid_colors.shape[-1]), 4, axis=0).flatten()


    def center_point(self):
        return Point(int(self.pnts_y/2), int(self.pnts_x/2))

    def draw_rect_into_grid(self, grid_colors, pnt: Point, width: int, height: int, color):
        half_w = int(width/2)
        half_h = int(height/2)
        x1 = max(pnt.x - half_w, 0)
        x2 = min(pnt.x + half_w, self.pnts_x - 1)
        y1 = max(pnt.y - half_h, 0)
        y2 = min(pnt.y + half_h, self.pnts_y - 1)

        grid_colors[x1:x2 + 1, y2, :] += color  # top    l->r
        grid_colors[x2, y1:y2, :] += color      # right  t->b
        grid_colors[x1+1:x2, y1, :] += color    # bottom l->r
        grid_colors[x1, y1:y2, :] += color      # left   t->b

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
