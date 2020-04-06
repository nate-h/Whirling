from schema import Schema, Or


SPECTROGRAM_SCHEMA = Schema(Or(dict, None))
