import os
import json
import time
import librosa
import logging

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


###############################################################################
# Loading Saving etc.
###############################################################################

def load_track(new_track: str):
    y, sr = librosa.load(new_track)
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
    y, sr = load_track(track)
    beats = get_beats(y, sr)
    volume_levels = get_volume_levels(y, sr)
    data = {
        'version': version,
        'beats': beats,
        #'volume_levels': volume_levels
    }
    save_features(track, data)
    return data

@timeit
def get_volume_levels(y, sr):
    volume_frames = librosa.feature.rms(y=y)
    volume_levels = librosa.frames_to_time(volume_frames, sr=sr)
    return volume_levels

@timeit
def get_beats(y, sr):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    logging.info('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    # 4. Convert the frame indices of beat events into timestamps
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    sustain = 0.2
    return [(b, b + sustain) for b in beat_times]
