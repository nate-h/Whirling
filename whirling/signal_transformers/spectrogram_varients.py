import librosa
from schema import Schema, Or


SPECTROGRAM_SCHEMA = Schema(Or(dict, None))


def generate(store, sig, spectrogram_settings):

    import pdb; pdb.set_trace()

    # Check if spectrogram is created already.
    if 'D' in store['signals'][sig]:
        return

    hop_length = store['plan']['metadata']['hop_length']
    n_fft = store['plan']['metadata']['n_fft']
    y = store['signals'][sig]['y']
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    store['signals'][sig]['D'] = D
