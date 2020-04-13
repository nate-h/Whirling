from whirling.visualizers.checkerboard_visualizer import CheckerboardVisualizer
from whirling.visualizers.debug_visualizer import DebugVisualizer
from whirling.visualizers.spectrogram_visualizer import SpectrogramVisualizer

VISUALIZERS = [
    ('Debug', DebugVisualizer),
    ('Checkerboard', CheckerboardVisualizer),
    ('Spectrogram', SpectrogramVisualizer),
]
