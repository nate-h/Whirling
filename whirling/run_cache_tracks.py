import logging
import argparse
import coloredlogs
from whirling.store import Store
from data.tracks import MUSIC_TRACKS
import tensorflow as tf
import multiprocessing


###############################################################################
# CacheTracks
###############################################################################

class CacheTracks(object):
    def __init__(self, plan, blast_cache=False):

        # Initialize store.
        self.store = Store.get_instance()
        self.store.initialize(plan, use_cache=False)

        tracks = self.get_unprocessed_tracks(MUSIC_TRACKS, blast_cache)

        logging.info('Number of tracks working on: %d', len(tracks))

        for t in tracks:
            logging.info('Processing track: %s', t)
            tf.keras.backend.clear_session()
            process_eval = multiprocessing.Process(target=run_track, args=(self.store, t))
            process_eval.start()
            process_eval.join()


    def get_unprocessed_tracks(self, tracks, blast_cache):
        if blast_cache:
            return tracks

        ret_tracks = []
        for t in tracks:
            if not self.store.store_cache_exists(t):
                ret_tracks.append(t)

        return ret_tracks

def run_track(store, t):
    store.current_track_bs.on_next(t)


###############################################################################
# Main and option handling.
###############################################################################

def parse_options():
    description = 'A python music visualizer using audio feature extraction'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--plan', type=str, default='default_plan',
                        help='A plan to generate data from a list of songs.')
    parser.add_argument('--blast-cache', default=False, action='store_true',
                        help='Erase and recreate track cache.')
    args = parser.parse_args()
    return args

def main():
    coloredlogs.install()

    args = parse_options()

    CacheTracks(args.plan, blast_cache=args.blast_cache)
