import os
import json
import time
import librosa
import logging
import sklearn

version = '0.0.2'


###############################################################################
# Helpers.
###############################################################################

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
# Feature extracting.
###############################################################################

@timeit
def generate_features(track: str):
    logging.info('Generating features for track: %s' % track)
    sr=22050
    hop_length = 512  # Note: may consider dropping this to 360 to get 60fps.
                      # Right now this equates to a 43fps resolution.
    y, sr = load_track(track, sr)

    ingredients = {
        'y': y,
        'sr': sr,
        'hop_length': hop_length,
    }

    data = {
        'metadata': {
            'version': version,
            'track': track,
            'sr': sr,
            'hop_length': hop_length,
        },
        'framed': {
            'frame_times':
                get_frame_times(**ingredients).tolist(),
            'rms':
                get_volume_levels(**ingredients).tolist(),
            'spectral_centroid':
                get_spectral_centroids(**ingredients).tolist(),
            'zero_crossing_rates':
                get_zero_crossing_rates(**ingredients).tolist(),
        },
        'events': {
            'beats':
                get_beats(**ingredients).tolist(),
        },
    }

    save_features(track, data)
    return data

@timeit
def get_frame_times(y, sr, hop_length):
    return librosa.samples_to_time(range(0, len(y), hop_length))

@timeit
def get_volume_levels(y, sr, hop_length):
    rms = librosa.feature.rms(y)[0]
    return normalize(rms)

@timeit
def get_spectral_centroids(y, sr, hop_length):
    spectral_centroids = librosa.feature.spectral_centroid(y, sr)[0]
    return normalize(spectral_centroids)

@timeit
def get_zero_crossing_rates(y, sr, hop_length):
    # Zero crossings are associated with percussive events.
    zcr = librosa.feature.zero_crossing_rate(y, sr)[0]
    return normalize(zcr)

@timeit
def get_beats(y, sr, hop_length):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    logging.info('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    return librosa.frames_to_time(beat_frames, sr=sr)
