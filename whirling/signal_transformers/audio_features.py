import os
import json
import librosa
import logging
import sklearn
import numpy as np
from schema import Schema, Optional


FEATURES_SCHEMA = Schema({
    Optional('full'): bool,
    Optional('harmonic'): bool,
    Optional('percussive'): bool,
    Optional('beats'): bool,
    Optional('onsets'): bool,
    Optional('frame_times'): bool,
    Optional('rms'): bool,
    Optional('spectral_centroid'): bool,
    Optional('spectral_flatness'): bool,
    Optional('zero_crossing_rates'): bool,
    Optional('onset_strength'): bool,
    Optional('loudness'): bool
})


###############################################################################
# Helpers.
###############################################################################

def get_events_at_time(current_track_audio_features, curr_time):
    beats = current_track_audio_features['beats']
    # See what beats should be played at curr_time
    return [b for b in beats if curr_time >= b[0] and curr_time < b[1]]


def normalize(x, axis=0):
    return sklearn.preprocessing.minmax_scale(x, axis=axis)


def get_frame_number(time, sr, hop_length):
    return librosa.core.time_to_frames([time], sr, hop_length)[0]


###############################################################################
# Feature extracting.
###############################################################################

def get_frame_times(y, D, sr, hop_length):
    return librosa.samples_to_time(range(0, len(y), hop_length), sr=sr)


def get_rms(y, D, sr, hop_length):
    rms = librosa.feature.rms(y, hop_length=hop_length)[0]
    return normalize(rms)


def get_spectral_centroids(y, D, sr, hop_length):
    spectral_centroids = librosa.feature.spectral_centroid(y, sr=sr, hop_length=hop_length)[0]
    return normalize(spectral_centroids)


def get_spectral_flatness(y, D, sr, hop_length):
    spectral_flatness = librosa.feature.spectral_flatness(y, hop_length=hop_length)[0]
    return normalize(spectral_flatness)


def get_zero_crossing_rates(y, D, sr, hop_length):
    # Zero crossings are associated with percussive events.
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
    return normalize(zcr)


def get_beats(y, D, sr, hop_length):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    logging.info('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    return beat_frames
    #return librosa.frames_to_time(beat_frames, sr=sr)


def get_onsets(y, D, sr, hop_length):
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
    return onsets
    #return librosa.frames_to_time(onsets, sr=sr)


def get_onset_strength(y, D, sr, hop_length):
    onset_strength = librosa.onset.onset_strength(y=y, sr=sr)
    return normalize(onset_strength)


def get_loudness(y, D, sr, hop_length):
    n_fft=2048
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    power = np.abs(S)**2
    p_mean = np.sum(power, axis=0, keepdims=True)
    p_ref = np.max(power)  # or whatever other reference power you want to use
    loudness = librosa.amplitude_to_db(p_mean, ref=p_ref)[0]
    return normalize(loudness)


def get_function_from_name(name):
    feature_extraction_fns = {
        'beats': get_beats,
        'onsets': get_onsets,
        'frame_times': get_frame_times,
        'rms': get_rms,
        'spectral_centroid': get_spectral_centroids,
        'spectral_flatness': get_spectral_flatness,
        'zero_crossing_rates': get_zero_crossing_rates,
        'onset_strength': get_onset_strength,
        'loudness': get_loudness
    }
    if name not in feature_extraction_fns:
        logging.info("Can't find feature extraction function %s", name)
        quit()
    return feature_extraction_fns[name]


def generate(store, sig, feature_name):
    y = store['signals'][sig]['y']
    D = store['signals'][sig]['D']
    sr = store['plan']['metadata']['sr']
    hop_length = store['plan']['metadata']['hop_length']
    fn = get_function_from_name(feature_name)
    store['signals'][sig]['features'][feature_name] = fn(y, D, sr, hop_length)
