"""The purpose of a store is to create a place to load, save, manage all of the
data involved with the visualizations.
At the heart of the store is a plan to specify the data sources each
visualization needs.
"""

import os
import json
import pickle
import logging
from typing import Dict, List
from rx.subject.behaviorsubject import BehaviorSubject

class Store:
    """What loads, saves and manages the data with all the visualizations"""
    def __init__(self, plan_name: str, current_track: BehaviorSubject,
                  use_cache: bool):
        self.plan_name = plan_name
        self.use_cache = use_cache
        self.store_data = None
        current_track.subscribe(self.on_track_change)

    def on_track_change(self, new_track):
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

    def generate_store(self, track_name):
        """Generates store data from """
        self.store_data = {
            'plan': self.load_plan()
        }

        print(self.signals)
        print(self.visualizers)
        import pdb; pdb.set_trace()

        # Get visualizers from plan
        # Update visualizers subject.
        # Get signals from plan
        # Need to get signals.
        # Save signals if plan wants it.
        return {}

    def get_visualizers(self, plan: Dict):
        pass

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
