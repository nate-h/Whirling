import math
import numpy as np
import librosa
from schema import Schema, Optional


SPECTROGRAM_SCHEMA = Schema({
    Optional('standard'): bool,
    Optional('custom_log_db'): bool,
})


def generate(store, sig, spectrogram_name):

    hop_length = store['plan']['metadata']['hop_length']
    n_fft = store['plan']['metadata']['n_fft']
    y = store['signals'][sig]['y']

    # Check if spectrogram is created already.
    if 'D' not in store['signals'][sig]:
        store['signals'][sig]['D'] = standard_spectrogram(y, n_fft, hop_length)

    D = store['signals'][sig]['D']

    if spectrogram_name == 'custom_log_db':
        store['signals'][sig]['spectrograms'][spectrogram_name] = \
            log_db_spectrogram(D)


def standard_spectrogram(y, n_fft, hop_length):
    return librosa.stft(y, n_fft=n_fft, hop_length=hop_length)


def log_db_spectrogram(D):
    """This function attempts to combine frequency bins non-uniformly.
    The non-uniform chunking is done by exponentially chunking up the
    bins. In other words, each chunk is exponentially larger than the last.
    Each chunk of frequency bins then gets there values averaged.
    """
    db_s = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    max_power = int(math.log(db_s.shape[0] - 1, 2))
    idxs = [(int(math.pow(2, (i-1)/12)), int(math.pow(2, i/12))) for i in range(max_power*12 + 1)
            if int(math.pow(2, (i-1)/12)) != int(math.pow(2, i/12))]
    log_db_s = np.array([
        [np.average(db_s[idx1: idx2, j]) for idx1, idx2 in idxs]
        for j in range(db_s.shape[1])
    ])
    return log_db_s