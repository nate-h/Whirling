"""The purpose of a store is to create a place to load, save, manage all of the
data involved with the visualizations.
At the heart of the store is a plan to specify the data sources each
visualization needs.
"""

import os
import json
import pickle
import logging
from typing import List
from rx.subject.behaviorsubject import BehaviorSubject
from schema import Schema, And, Optional, Or
from whirling.visualizers import VALID_VISUALIZERS
from whirling.signal_transformers import VALID_SIGNALS
from whirling.signal_transformers.audio_features import FEATURES_SCHEMA
from whirling.signal_transformers.spectrograms import SPECTROGRAM_SCHEMA
from whirling.signal_transformers import signal_dissectors

class Store:
    """What loads, saves and manages the data with all the visualizations"""
    def __init__(self, plan_name: str, current_track: BehaviorSubject,
                  use_cache: bool):
        self.plan_name = plan_name
        self.use_cache = use_cache
        self.store_data = None
        current_track.subscribe(self.on_track_change)

    def on_track_change(self, new_track):
        if new_track == '':
            return

        exist = self.store_cache_exists(new_track)

        if not exist or not self.use_cache:
            self.generate_store(new_track)
            self.save_store(new_track, self.store_data)
        else:
            self.store_data = self.load_store(new_track)

    @property
    def plan(self):
        if self.store_data is None:
            return None
        return self.store_data['plan']

    @property
    def visualizers(self) -> List[str]:
        if not self.plan:
            logging.error('No plan found.')
            quit()
        return list(self.plan['visualizers'].keys())

    @property
    def signals(self) -> List[str]:
        if not self.plan:
            logging.error('No plan found.')
            quit()
        signals = set()
        for _v, v_obj in self.plan['visualizers'].items():
            signals.update(v_obj['signals'].keys())
        return list(signals)

    def get_visualizer_plan(self, visualizer_name):
        if visualizer_name not in self.plan['visualizers']:
            logging.error('Couldn\'t find visualizer plan %s', visualizer_name)
            quit()
        return self.plan['visualizers'][visualizer_name]

    def load_plan(self):
        """Load data generation plan."""
        full_plan_loc = f'plans/{self.plan_name}.json'
        if not os.path.exists(full_plan_loc):
            logging.error('Couldn\'t find plan %s', full_plan_loc)
            quit()
        with open(full_plan_loc, 'r') as f:
            return json.load(f)

    def validate_plan(self):
        """Using the schema package, validate the basics for a plan.
        Each individual visualizer will finish checking the plan respectively
        for their specific settings."""
        schema = Schema(
            {
                "metadata": {
                    "sr": int,
                    "hop_length": int,
                    "n_fft": int,
                    Optional("save_signals"): bool
                },
                "visualizers": {
                    And(str, lambda n: n in VALID_VISUALIZERS): {
                        "settings": dict,
                        "signals": {
                            And(str, lambda n: n in VALID_SIGNALS): {
                                Optional('spectrogram'): SPECTROGRAM_SCHEMA,
                                Optional('features'): FEATURES_SCHEMA,
                            }
                        }
                    }
                }
            }
        )
        schema.validate(self.plan)

    def merge_plan_signal_defs(self):
        """Merge the signal json blobs of all plan visualizers.
        This makes data generation much easier down the road by not repeating
        work. Each visualizer can then access the plan and get the necessary
        data to render."""
        merged = {}
        for v, v_obj in self.plan['visualizers'].items():
            for s, s_obj in v_obj['signals'].items():
                if s not in merged:
                    merged[s] = {}
                # Merge feature data request.
                if 'features' in s_obj:
                    if 'features' not in merged[s]:
                        merged[s]['features'] = {}
                    for f, use in s_obj['features'].items():
                        if use:
                            merged[s]['features'][f] = None
                # Merge spectrogram data request.
                if 'spectrogram' in s_obj:
                    if 'spectrogram' not in merged[s]:
                        merged[s]['spectrogram'] = None
        return {'signals': merged}

    def generate_store(self, track_name):
        """Generates store data from """
        self.store_data = {
            'plan': self.load_plan()
        }
        self.validate_plan()
        merged_signal_data_defs = self.merge_plan_signal_defs()
        self.store_data.update(merged_signal_data_defs)

        # TODO: inform visualizer controller of intended visualizers (via subject?).

        # Generate signals
        sigs = list(self.store_data['signals'].keys())
        for sig_name in sigs:
            signal_dissectors.generate(track_name, self.store_data, sig_name)

        # Save signals
        # Have each signal ready
        # Process features
        # process spectrograms.

        import pdb; pdb.set_trace()
        return {}

    def store_file_name(self, track_name: str) -> str:
        """Constructs store file name from track name"""
        return f'{os.path.splitext(track_name)[0]}_{self.plan_name}.p'

    def store_cache_exists(self, track_name: str) -> bool:
        """Checks if cache exists for the combination of plan and track name."""
        pickle_name = self.store_file_name(track_name)
        return os.path.exists(pickle_name)

    def save_store(self, track_name, store) -> None:
        """Cache store as a pickle."""
        pickle_name = self.store_file_name(track_name)
        with open(pickle_name, "wb") as f:
            pickle.dump(store, f)

    def load_store(self, track_name):
        """Load pickled store."""
        pickle_name = self.store_file_name(track_name)
        with open(pickle_name, "rb") as f:
            return pickle.load(f)
