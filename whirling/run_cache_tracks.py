"""Whirling

Use this program to generate the audio features and track segmentations for an
audio clip.
Start with `run_cache_tracks --help`
"""

import logging
import argparse
import multiprocessing
import coloredlogs
import tensorflow as tf
from data.tracks import MUSIC_TRACKS
from whirling.store import Store


###############################################################################
# run_cache_tracks
###############################################################################

class CacheTracks():
    """Generates precached dnz files.
    A dnz file contains the extracted features and track segmentations for a
    an audio clip. The generated features and segmentations are specified in
    plans.
    """

    def __init__(self):
        """Initialize class"""
        # Parse options.
        args = parse_options()
        plan = args.plan
        blast_cache = args.blast_cache

        # Initialize store.
        self.store = Store.get_instance()
        self.store.initialize(plan, use_cache=False)

        # Find unprocessed tracks then generate dnz files for them.
        tracks = self.get_unprocessed_tracks(MUSIC_TRACKS, blast_cache)
        self.generate_dnz_files(tracks)

    def generate_dnz_files(self, tracks):
        """Iterates on tracks while generating the dnz files."""
        logging.info('Number of tracks working on: %d', len(tracks))

        for track in tracks:
            logging.info('Processing track: %s', track)
            tf.keras.backend.clear_session()
            process_eval = multiprocessing.Process(
                target=run_track, args=(self.store, track))
            process_eval.start()
            process_eval.join()


    def get_unprocessed_tracks(self, tracks, blast_cache):
        """Determines what tracks don't have dnz files yet."""
        if blast_cache:
            return tracks

        ret_tracks = []
        for track in tracks:
            if not self.store.store_cache_exists(track):
                ret_tracks.append(track)

        return ret_tracks

###############################################################################
# Helpers.
###############################################################################

def parse_options():
    """Define argparse options."""
    description = "This program generates the audio features and track" \
        " segmentations for a specified plan on all tracks."
    epilog = "Usage: run_cache_tracks --plan default_plan"
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--plan', type=str, default='default_plan',
                        help='A plan to generate data from a list of songs.')
    parser.add_argument('--blast-cache', default=False, action='store_true',
                        help='Erase and recreate track cache.')
    args = parser.parse_args()
    return args


def run_track(store, track):
    """Kicks off the dnz file generation process."""
    store.current_track_bs.on_next(track)


###############################################################################
# Main and option handling.
###############################################################################

def main():
    """Initialize the program."""
    coloredlogs.install()
    CacheTracks()
