"""Establish what the valid visualizers are."""

from whirling.visualizers.debug_visualizer import DebugVisualizer
from whirling.visualizers.checkerboard_visualizer import CheckerboardVisualizer
from whirling.visualizers.spectrogram_visualizer import SpectrogramVisualizer

_visualizers = [DebugVisualizer, CheckerboardVisualizer, SpectrogramVisualizer]
VALID_VISUALIZERS = [
    v.__name__.replace('Visualizer', '').lower() for v in _visualizers
]
