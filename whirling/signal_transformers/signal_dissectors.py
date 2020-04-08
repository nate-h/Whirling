import librosa
import logging

def generate(track_name: str, store, signal_name: str):

    plan = store['plan']

    # Get default track name.
    # Load track
    y, sr, D = load_track(track_name, plan)

    # If signal name is full, bail.
    if signal_name is 'full':
        return

    if signal_name in ["harmonic", "percussive"]:
        pass
    elif signal_name in ["vocals", "base", "drums", "other"]:
        pass

def load_track(track_name, plan):
    logging.info('Generating features for track: %s', track_name)
    sr = plan['metadata']['sr']
    hop_length = plan['metadata']['hop_length']
    n_fft = plan['metadata']['n_fft']
    y, sr = librosa.load(track_name, sr=sr)
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    return y, sr, D