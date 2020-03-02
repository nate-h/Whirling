from whirling.checkerboard_visualizer.checkerboard_visualizer import CheckerboardVisualizer
from whirling.debug_visualizer.debug_visualizer import DebugVisualizer
from whirling.spectrogram_visualizer.spectrogram_visualizer import SpectrogramVisualizer

visualizers = [
    ('Debug', DebugVisualizer),
    ('Checkerboard', CheckerboardVisualizer),
    ('Spectrogram', SpectrogramVisualizer),
]