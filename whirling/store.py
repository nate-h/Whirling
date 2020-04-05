"""The purpose of a store is to create a place to load, save, manage all of the
data involved with the visualizations.
At the heart of the store is a plan to specify the data sources each
visualization needs.
"""

import os
import json
import logging

class Store:
    """What loads, saves and manages the data with all the visualizations"""
    def __init__(self):
        pass

    def load_plan(self, plan_name):
        full_plan_loc = 'plans/{}.json'.format(plan_name)
        if not os.path.exists(full_plan_loc):
            logging.error('Couldn\'t find plan %s', full_plan_loc)
            quit()
        with open(full_plan_loc, 'r') as f:
            return json.load(f)

    def save_pickle(self, track_name, store):
        pass

    def load_pickle(self, track_name):
        pass

    def does_pickle_exist(self, track_name):
        pass

    def track_to_pickle_name(self, track_name):
        pass


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
