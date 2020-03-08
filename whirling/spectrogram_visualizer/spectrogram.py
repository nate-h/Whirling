import time
import math
import librosa
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders
import numpy as np
from whirling import colors
from whirling.ui_visualizer_base import UIVisualizerBase
from whirling.ui_audio_controller import UIAudioController
from matplotlib import cm
from whirling import viridis


class Spectrogram():
    def __init__(self, parent_rect):

        # length of the windowed signal after padding with zeros
        self.n_fft = 2048

        self.log_db_s = self.create_log_db_spectrogram()
        self.pnts_x, self.pnts_y = self.log_db_s.shape
        self.create_vbo_data()
        self.shader = self.initialize_shader()

    def create_log_db_spectrogram(self):
        # Extract 8s clip from signal y and run a stft on it.
        timer_start = time.time()
        curr_time = self.audio_controller.get_time()
        curr_window_number = math.floor(curr_time/self.seconds_worth)
        min_window_time = curr_window_number * self.seconds_worth
        max_window_time = (curr_window_number + 1) * self.seconds_worth

        # start_y = librosa.time_to_samples([min_window_time], sr=self.sr)[0]
        # end_y = librosa.time_to_samples([max_window_time], sr=self.sr)[0]

        #import pdb; pdb.set_trace()
        # FIXME: GET ACTUAL SONG.
        y_sample, _sr = librosa.load('data/latch.mp3', sr=self.sr,
            offset=min_window_time, duration=max_window_time-min_window_time)

        n_fft=2048
        D = librosa.stft(y_sample, n_fft=n_fft)

        # Convert amplitude spec to DB spec.
        db_s = librosa.amplitude_to_db(np.abs(D), ref=np.max)

        # Take our n frequency bins D has and logarithmically chunk them up.
        # Each chunk is exponentially larger than the last.
        # Each chunk of frequency bins then gets there values averaged.
        max_power = int(math.log(db_s.shape[0] - 1, 2))
        idxs = [(int(math.pow(2, (i-1)/12)), int(math.pow(2, i/12))) for i in range(max_power*12 + 1)
                if int(math.pow(2, (i-1)/12)) != int(math.pow(2, i/12))]
        log_db_s = np.array([
            [np.average(db_s[idx1: idx2, j]) for idx1, idx2 in idxs]
            for j in range(db_s.shape[1])
        ])
        print(f'log_db_s.shape: {log_db_s.shape}')
        print(f'Total time for create_db_spectrogram: {time.time() - timer_start}')

        return log_db_s

    def draw(self):
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

    def create_vbo_data(self):
        h = self.height/3
        sw = self.width / self.pnts_x
        sh = h / self.pnts_y
        swl = 0.0 * sw
        swr = 1.0 * sw
        shl = 0.0 * sh
        shr = 1.0 * sh

        # Define plot parameters.
        rectangle = []
        indices = []
        count = 0

        # Generate rects and indices for triangles in rect.
        for i in range(self.pnts_x):
            for j in range(self.pnts_y):
                x = i * sw
                y = j * sh
                signal_strength = max(min((self.log_db_s[i, j] + 80)/80, 1), 0)
                c = viridis.get_color(signal_strength)

                x1 = round(self.rect.left   + x + swl)
                x2 = round(self.rect.left   + x + swr)
                y1 = round(self.rect.bottom + y + shl)
                y2 = round(self.rect.bottom + y + shr)

                # Add 2 triangles to create a rect.
                rectangle.extend(
                    [
                        # Position     # Color
                        x1, y1, 0.0,   c[0], c[1], c[2],
                        x2, y1, 0.0,   c[0], c[1], c[2],
                        x2, y2, 0.0,   c[0], c[1], c[2],
                        x1, y2, 0.0,   c[0], c[1], c[2],
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
        return OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )