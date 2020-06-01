"""Establish what the valid visualizers are."""

import re
from whirling.visualizers.debug_visualizer import DebugVisualizer
from whirling.visualizers.spectrogram_visualizer import SpectrogramVisualizer
from whirling.visualizers.checkerboard_visualizer import CheckerboardVisualizer
from whirling.visualizers.stacked_equalizers_visualizer import StackedEqualizersVisualizer
from whirling.visualizers.combo_board_visualizer import ComboBoardVisualizer

# Listify visualizer classes.
_visualizers = [
    DebugVisualizer, SpectrogramVisualizer, CheckerboardVisualizer,
    StackedEqualizersVisualizer, ComboBoardVisualizer
]

# Create tuples of (visualizer name, visualizer class).
VISUALIZERS = [
    (
        re.sub( '(?<!^)(?=[A-Z])', '_', v.__name__.replace('Visualizer', '')).lower(),
        v
    ) for v in _visualizers
]
