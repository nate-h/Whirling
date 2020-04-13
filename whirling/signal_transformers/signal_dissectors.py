import numpy as np
import librosa
import logging
from spleeter.separator import Separator

def generate(track_name: str, store, signal_name: str) -> None:

    plan = store['plan']

    # Load track if not already loaded.
    if not has_loaded_track(store):
        load_track_into_store(track_name, plan, store)

    # Get full track signal, D, sr.
    y = store['signals']['full']['y']
    D = store['signals']['full']['D']

    # If signal name is full, bail.
    if signal_name is 'full':
        return

    # Bail if we already have some data from this segmentation.
    if already_ran_segmenter(store, signal_name):
        return

    # Segment signals.
    if signal_name in ["librosa_harmonic", "librosa_percussive"]:
        segment_harmonics_percussives(store, D)
    elif signal_name in ['spleeter_' + f for f in ['vocals', 'drums', 'base', 'other']]:
        segment_signal_with_spleeter(store, y, track_name)


def has_loaded_track(store) -> bool:
    """Determines if the store has the full signal y loaded."""
    return 'y' in store['signals']['full']


def load_track_into_store(track_name: str, plan, store) -> None:
    logging.info('Generating features for track: %s', track_name)
    sr = plan['metadata']['sr']
    hop_length = plan['metadata']['hop_length']
    n_fft = plan['metadata']['n_fft']
    y, sr = librosa.load(track_name, sr=sr)
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    store['signals']['full']['y'] = y
    store['signals']['full']['D'] = D


def segment_harmonics_percussives(store, D):
    """HPSS generates two audio signals. One for the harmonics and the
    other for the percussives."""
    margin = 2
    DH, DP = librosa.decompose.hpss(D, margin=margin)

    # Add segmented signals to the store.
    add_signal(store, 'librosa_harmonic', librosa.istft(DH), DH)
    add_signal(store, 'librosa_percussive', librosa.istft(DP), DP)


def segment_signal_with_spleeter(store, y, track_name):
    return

    # TODO: pull spleeter when it's fixed.

    """Use spleeter to separate the track into 4 components:
    Vocals, Drums, base, other separation"""

    # Slap two monotone signals to make a stereo signal.
    y_new = np.array([y, y]).T

    separator = Separator('spleeter:4stems')
    prediction = separator.separate(y_new, track_name)

    # Add segmented signals to the store.
    add_signal(store, 'spleeter_other', prediction['other'][:, 0])
    add_signal(store, 'spleeter_drums', prediction['drums'][:, 0])
    add_signal(store, 'spleeter_bass', prediction['bass'][:, 0])
    add_signal(store, 'spleeter_vocals', prediction['vocals'][:, 0])

def already_ran_segmenter(store, signal_name: str) -> bool:
    """Return wether or not the store has any separated signal data."""
    if signal_name not in store['signals']:
        return False

    return 'y' in store['signals'][signal_name]

def add_signal(store, signal_name, y, D=None):
    if signal_name not in store['signals']:
        store['signals'][signal_name] = {
            'y': None,
            'D': None
        }
    store['signals'][signal_name]['y'] = y
    store['signals'][signal_name]['D'] = D
