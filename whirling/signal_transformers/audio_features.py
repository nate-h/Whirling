import os
import json
import librosa
import logging
import sklearn
import numpy as np
import pkg_resources  # part of setuptools
from whirling.plan import load_plan


###############################################################################
# Helpers.
###############################################################################

def get_version():
    return pkg_resources.require("Whirling")[0].version

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

def audio_to_feature_file(track: str, plan: str):
    return f'{os.path.splitext(track)[0]}_{plan}.json'

def cache_exists(track: str, plan: str):
    return os.path.exists(audio_to_feature_file(track, plan))

def load_features(track: str, plan: str):
    logging.info('Loading cached features for track: %s' % track)
    if not cache_exists(track, plan):
        logging.info('No cache saved for this file. Generating features now.')
        return run_plan(plan, track)
    else:
        with open(audio_to_feature_file(track, plan), 'r') as f:
            return json.load(f)

def save_features(track: str, data: any, plan: str):
    feature_file = audio_to_feature_file(track, plan)
    # TODO
    with open(feature_file, 'w') as f:
        json.dump(data, f, indent=4)


###############################################################################
# Track separation.
###############################################################################

def get_full_audio_signal(store, settings):
    """Full is the regular audio signal"""
    store['audio_signals']['full'] = {
        'y': store['y'],
        'D': store['D'],
    }

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
    return librosa.frames_to_time(beat_frames, sr=sr)

def get_onsets(y, D, sr, hop_length):
    onsets = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
    return librosa.frames_to_time(onsets, sr=sr)

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


###############################################################################
# Gateway method.
###############################################################################

def run_plan(plan_name:str, track: str):

    loaded_plan = load_plan(plan_name)

    # Establish basic properties.
    logging.info('Generating features for track: %s' % track)
    sr = 22050
    n_fft = 2048
    hop_length = 512  # Note: may consider dropping this to 360 to get 60fps.
                      # Right now this equates to a 43fps resolution.
    y, sr = load_track(track, sr)
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
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
    for audio_signal_def in loaded_plan['audio_signals']:
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

    save_features(track, data, plan_name)
    return data


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
        'onset_strength': get_onset_strength,
        'loudness': get_loudness
    }
