import librosa
from schema import Schema, Or


SPECTROGRAM_SCHEMA = Schema(Or(dict, None))


def generate(store, sig, spectrogram_settings):

    # Check if spectrogram is created already.
    if 'D' in store['signals'][sig]:
        return

    # Generate and populate store with the spectrogram for this signal.
    hop_length = store['plan']['metadata']['hop_length']
    n_fft = store['plan']['metadata']['n_fft']
    y = store['signals'][sig]['y']
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    store['signals'][sig]['D'] = D
