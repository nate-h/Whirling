import os
import json
import time
import librosa
import logging
import sklearn
import numpy as np
import pkg_resources  # part of setuptools


###############################################################################
# Helpers.
###############################################################################

def get_version():
    return pkg_resources.require("Whirling")[0].version

def timeit(method):
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        logging.info('Method `%s` took %f seconds to run' % (
            method.__name__, (te-ts)))
        return result
    return timed

def get_events_at_time(current_track_audio_features, curr_time):
    beats = current_track_audio_features['beats']
    # See what beats should be played at curr_time
    return [b for b in beats if curr_time >= b[0] and curr_time < b[1]]

def normalize(x, axis=0):
    return sklearn.preprocessing.minmax_scale(x, axis=axis)

def get_frame_number(time, sr, hop_length):
    return librosa.core.time_to_frames([time], sr, hop_length)[0]


###############################################################################
# Loading Saving etc.
###############################################################################

def load_track(new_track: str, sr:int=22500):
    y, sr = librosa.load(new_track, sr=sr)
    return y, sr

def audio_to_feature_file(track: str):
    return os.path.splitext(track)[0] + '.json'

def cache_exists(track: str):
    return os.path.exists(audio_to_feature_file(track))

def load_features(track: str):
    logging.info('Loading cached features for track: %s' % track)
    if not cache_exists(track):
        logging.error('No cache saved for this file.')
    else:
        with open(audio_to_feature_file(track), 'r') as f:
            return json.load(f)

def save_features(track: str, data):
    feature_file = audio_to_feature_file(track)
    with open(feature_file, 'w') as f:
        json.dump(data, f, indent=4)


###############################################################################
# Signal modifying.
###############################################################################

@timeit
def get_full_audio_signal(store, settings):
    """Full is the regular audio signal"""
    store['audio_signals']['full'] = {
        'y': store['y'],
        'D': store['D'],
    }

@timeit
def get_hpss_audio_signal(store, settings):
    audio_signals = store['audio_signals']
    if 'harmonic' in audio_signals and 'harmonic' in audio_signals:
        return
    """HPSS generates two audio signals. One for the harmonics and the
    other for the percussives."""
    DH, DP = librosa.decompose.hpss(store['D'], margin=settings['margin'])
    audio_signals.update({
        'harmonic': {
            'y': librosa.istft(DH),
            'D': DH,
        },
        'percussive': {
            'y': librosa.istft(DP),
            'D': DP,
        }
    })


###############################################################################
# Feature extracting.
###############################################################################

@timeit
def get_frame_times(y, D, sr, hop_length):
    return librosa.samples_to_time(range(0, len(y), hop_length), sr=sr)

@timeit
def get_rms(y, D, sr, hop_length):
    rms = librosa.feature.rms(y, hop_length=hop_length)[0]
    return normalize(rms)

@timeit
def get_spectral_centroids(y, D, sr, hop_length):
    spectral_centroids = librosa.feature.spectral_centroid(y, sr=sr, hop_length=hop_length)[0]
    return normalize(spectral_centroids)

@timeit
def get_spectral_flatness(y, D, sr, hop_length):
    spectral_flatness = librosa.feature.spectral_flatness(y, hop_length=hop_length)[0]
    return normalize(spectral_flatness)

@timeit
def get_zero_crossing_rates(y, D, sr, hop_length):
    # Zero crossings are associated with percussive events.
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
    return normalize(zcr)

@timeit
def get_beats(y, D, sr, hop_length):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    logging.info('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    return librosa.frames_to_time(beat_frames, sr=sr)

@timeit
def get_onsets(y, D, sr, hop_length):
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
    return librosa.frames_to_time(onsets, sr=sr)

@timeit
def get_onset_strength(y, D, sr, hop_length):
    onset_strength = librosa.onset.onset_strength(y=y, sr=sr)
    return normalize(onset_strength)

@timeit
def get_loudness(y, D, sr, hop_length):
    S = librosa.stft(y, hop_length=hop_length)
    D = librosa.amplitude_to_db(S, ref=np.max)


###############################################################################
# Gateway method.
###############################################################################

@timeit
def generate_features(plan, music_tracks, use_cache):
    for track in music_tracks:
        if use_cache and cache_exists(track):
            continue
        run_plan(plan, track)


def run_plan(plan:str, track: str):

    # Establish basic properties.
    logging.info('Generating features for track: %s' % track)
    sr = 22050
    n_fft = 2048
    hop_length = 512  # Note: may consider dropping this to 360 to get 60fps.
                      # Right now this equates to a 43fps resolution.
    y, sr = load_track(track, sr)
    D = librosa.stft(y, n_fft=n_fft)
    fn_mappings = get_function_mappings()
    data = {
        "metadata": {
            'sr': sr,
            'hop_length': hop_length,
            'track': track
        },
        "audio_signals": {}
    }

    # Initialize store.
    store = {
        'y': y,
        'sr': sr,
        'D': D,
        'hop_length': hop_length,
        'audio_signals': {}
    }

    # Generate all audio signals and their feature extractions.
    # Note: certain defs may export 1+ audio signals like hpss.
    for audio_signal_def in plan['audio_signals']:
        signal_name = audio_signal_def['name']
        settings = audio_signal_def['settings']
        extracts = audio_signal_def['extracts']

        # Generate audio signal.
        fn_mappings[signal_name](store, settings)

        # Get audio signal.
        y = store['audio_signals'][signal_name]['y']
        D = store['audio_signals'][signal_name]['D']

        data['audio_signals'][signal_name] = {
            'description': audio_signal_def['description'],
            'settings': settings,
            'extracts': {k: {} for k,_v in extracts.items()}
        }
        for event_type, event_list in extracts.items():
            for fn_name in event_list:
                data['audio_signals'][signal_name]['extracts'][event_type][fn_name] = \
                    fn_mappings[fn_name](y, D, sr, hop_length).tolist()

    save_features(track, data)


def get_function_mappings():
    return {
        'full': get_full_audio_signal,
        'harmonic': get_hpss_audio_signal,
        'percussive': get_hpss_audio_signal,
        'beats': get_beats,
        'onsets': get_onsets,
        'frame_times': get_frame_times,
        'rms': get_rms,
        'spectral_centroid': get_spectral_centroids,
        'spectral_flatness': get_spectral_flatness,
        'zero_crossing_rates': get_zero_crossing_rates,
        'onset_strength': get_onset_strength
    }
