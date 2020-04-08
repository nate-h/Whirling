import librosa
import logging

def generate(track_name: str, store, signal_name: str) -> None:

    plan = store['plan']

    # Load track if not already loaded.
    if not has_loaded_track(store):
        load_track_into_store(track_name, plan, store)

    # Get full track signal, D, sr.
    y = store['signals']['full']['y']
    D = store['signals']['full']['D']
    sr = plan['metadata']['sr']

    # If signal name is full, bail.
    if signal_name is 'full':
        return

    if signal_name in ["librosa_harmonic", "librosa_percussive"]:
        segment_harmonics_percussives(D, store)
    elif signal_name in ["vocals", "base", "drums", "other"]:
        pass


def has_loaded_track(store) -> bool:
    """Determines if the store has the full signal y loaded."""
    return 'y' in store['signals']['full']


def load_track_into_store(track_name, plan, store) -> None:
    logging.info('Generating features for track: %s', track_name)
    sr = plan['metadata']['sr']
    hop_length = plan['metadata']['hop_length']
    n_fft = plan['metadata']['n_fft']
    y, sr = librosa.load(track_name, sr=sr)
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    store['signals']['full']['y'] = y
    store['signals']['full']['D'] = D

def segment_harmonics_percussives(D, store):
    """HPSS generates two audio signals. One for the harmonics and the
    other for the percussives."""
    margin = 2
    DH, DP = librosa.decompose.hpss(D, margin=margin)
    store['signals']['librosa_harmonic']['y'] = librosa.istft(DH)
    store['signals']['librosa_harmonic']['D'] = DH
    store['signals']['librosa_percussive']['y'] = librosa.istft(DP)
    store['signals']['librosa_percussive']['D'] = DP


def get_spleeter_audio_signal(store, settings):

    # Establish what signals spleeter will parse.
    spleeter_signals = {
        'spleeter_' + f for f in ['vocals', 'drums', 'base', 'other']}

    # Get full list of audio signals we've extracted already.
    audio_signals = set(list(store['audio_signals'].keys()))

    # Don't proceed if lists overlap at all.
    if len(spleeter_signals & audio_signals) > 0:
        return


    """Use spleeter to separate the track into 4 components:
    Vocals, Drums, base, other separation"""

    pass

