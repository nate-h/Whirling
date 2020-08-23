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
import pkg_resources  # part of setuptools
from rx.subject.behaviorsubject import BehaviorSubject
from schema import Schema, And, Optional
from whirling.signal_transformers import VALID_SIGNALS
from whirling.signal_transformers import audio_features
from whirling.signal_transformers import spectrogram_variants
from whirling.signal_transformers import signal_dissectors


class Store():
    """What loads, saves and manages the data with all the visualizations"""

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Store.__instance is None:
            Store()
        return Store.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Store.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Store.__instance = self

            # Declare what variables this store intends to have.
            self.current_track_bs: BehaviorSubject = None
            self.current_visualizer_bs: BehaviorSubject = None
            self.is_plan_loaded_bs: BehaviorSubject = None
            self.plan_name: str = None
            self.use_cache: bool = None

            # The plan output contains the output from processing the plan.
            self.plan_output = None

    def initialize(self, plan_name: str, use_cache: bool):
        """Setup store"""
        self.plan_name = plan_name
        self.use_cache = use_cache

        # Initialize behavior subjects.
        self.is_plan_loaded_bs = BehaviorSubject(False)
        self.current_track_bs = BehaviorSubject('')
        self.current_track_bs.subscribe(self.on_track_change)
        self.current_visualizer_bs = BehaviorSubject('')

        # audio
        # method for audio_get_time

    def on_track_change(self, new_track):
        """On track change, get either generate data or load cached data."""

        # Reset information.
        self.is_plan_loaded_bs.on_next(False)
        self.plan_output = None

        if new_track == '':
            return

        exist = self.store_cache_exists(new_track)

        if not exist or not self.use_cache:
            self.generate_plan_output(new_track)
            self.save_store(new_track, self.plan_output)
        else:
            self.plan_output = self.load_store(new_track)

        # Notify others the plan is loaded.
        self.is_plan_loaded_bs.on_next(True)

    @property
    def plan(self):
        """Grab plan from dnz output."""
        if self.plan_output is None:
            return None
        return self.plan_output['plan']

    @property
    def visualizers(self) -> List[str]:
        """Grab visualizers from dnz file."""
        if not self.plan:
            logging.error('No plan found.')
            quit()
        return list(self.plan['visualizers'].keys())

    @property
    def signals(self) -> List[str]:
        """Grab signal names from plan."""
        if not self.plan:
            logging.error('No plan found.')
            quit()
        signals = set()
        for _v, v_obj in self.plan['visualizers'].items():
            signals.update(v_obj['signals'].keys())
        return list(signals)

    @property
    def signal_features(self):
        """Grab loaded features per signal."""
        signal_features = {}
        for _v, v_obj in self.plan['visualizers'].items():
            for s, s_obj in v_obj['signals'].items():
                if 'features' in s_obj:
                    features = set([f for f, b in s_obj['features'].items() if b])
                    if s not in signal_features:
                        signal_features[s] = set()
                    signal_features[s].update(features)
        return signal_features

    @property
    def signal_spectrograms(self):
        """Find out which signals want a spectrogram."""
        signal_spectrograms = {}
        for _v, v_obj in self.plan['visualizers'].items():
            for s, s_obj in v_obj['signals'].items():
                if 'spectrograms' in s_obj:
                    spectrograms = set([f for f, b in s_obj['spectrograms'].items() if b])
                    if s not in signal_spectrograms:
                        signal_spectrograms[s] = set()
                    signal_spectrograms[s].update(spectrograms)
        return signal_spectrograms

    def load_plan(self):
        """Generate the plan output aka dnz (dance) file from the plan."""
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

        # FIXME: Hack to get around circular import.
        from whirling.visualizers import VISUALIZERS

        schema = Schema(
            {
                "metadata": {
                    "sr": int,
                    "hop_length": int,
                    "n_fft": int,
                    Optional("save_signals"): bool
                },
                "visualizers": {
                    And(str, lambda n: n in [v[0] for v in VISUALIZERS]): {
                        "settings": dict,
                        "signals": {
                            And(str, lambda n: n in VALID_SIGNALS): {
                                Optional('spectrograms'): spectrogram_variants.SPECTROGRAM_SCHEMA,
                                Optional('features'): audio_features.FEATURES_SCHEMA,
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
        for _, v_obj in self.plan['visualizers'].items():
            for sig_name, s_obj in v_obj['signals'].items():
                if sig_name not in merged:
                    merged[sig_name] = {}
                # Merge feature data request.
                if 'features' in s_obj:
                    if 'features' not in merged[sig_name]:
                        merged[sig_name]['features'] = {}
                    for f, use in s_obj['features'].items():
                        if use:
                            merged[sig_name]['features'][f] = None
                # Merge spectrogram data request.
                if 'spectrograms' in s_obj:
                    if 'spectrograms' not in merged[sig_name]:
                        merged[sig_name]['spectrograms'] = {}
                    for s, use in s_obj['spectrograms'].items():
                        if use:
                            merged[sig_name]['spectrograms'][s] = None
        return {'signals': merged}

    def generate_plan_output(self, track_name):
        """Generates store data from """
        self.plan_output = {
            'plan': self.load_plan()
        }
        self.validate_plan()
        merged_signal_data_defs = self.merge_plan_signal_defs()
        self.plan_output.update(merged_signal_data_defs)

        # Generate signals
        sigs = self.signals
        for sig_name in sigs:
            signal_dissectors.generate(track_name, self.plan_output, sig_name)

        # Generate spectrogram.
        for sig, spectrograms in self.signal_spectrograms.items():
            for s in spectrograms:
                spectrogram_variants.generate(self.plan_output, sig, s)

        # Generate features.
        for sig, features in self.signal_features.items():
            for f in features:
                audio_features.generate(self.plan_output, sig, f)

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

        # Delete full spectrogram since log based one is much smaller.
        # I may add this back and this is a short term solution to drastically
        # reducing pickle size.
        for s in store['signals'].keys():
            del store['signals'][s]['D']
            store['signals'][s]['D'] = None

        with open(pickle_name, "wb") as f:
            pickle.dump(store, f)

    def load_store(self, track_name):
        """Load pickled store."""
        pickle_name = self.store_file_name(track_name)
        with open(pickle_name, "rb") as f:
            return pickle.load(f)
