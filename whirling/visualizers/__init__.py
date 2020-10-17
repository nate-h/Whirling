"""Establish what the valid visualizers are."""

import re
from whirling.visualizers.debug_visualizer import DebugVisualizer
from whirling.visualizers.spectrogram_visualizer import SpectrogramVisualizer
from whirling.visualizers.concentric_squares import ConcentricSquares
from whirling.visualizers.stacked_equalizers_visualizer import StackedEqualizersVisualizer
from whirling.visualizers.combo_board_visualizer import ComboBoardVisualizer
from whirling.visualizers.checkerboard_visualizer import CheckerboardVisualizer

# Listify visualizer classes.
_visualizers = [
    DebugVisualizer, SpectrogramVisualizer, StackedEqualizersVisualizer,
    ConcentricSquares, CheckerboardVisualizer, ComboBoardVisualizer
]

# Create tuples of (visualizer name, visualizer class).
VISUALIZERS = [
    (
        re.sub('(?<!^)(?=[A-Z])', '_', v.__name__.replace('Visualizer', '')).lower(),
        v
    ) for v in _visualizers
]

def find_visualizer_class(vis_name):
    """Get visualizer class from name."""
    return list(filter(lambda x: x[0] == vis_name, VISUALIZERS))[0][1]
