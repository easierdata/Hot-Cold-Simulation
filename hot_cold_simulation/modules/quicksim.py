import concurrent.futures
import pickle
from multiprocessing import cpu_count
from pathlib import Path
from typing import Any, Dict

import numpy as np
from modules.lru_cache import LRUCache  # type: ignore


class MonteCarloSimulation:
    def __init__(
        self,
        regions_count: int,
        states_count: int,
        counties_count: int,
        weights: list[float],
        num: int,
        hot_layer_constraint: int,
        preload_data: bool = False,
    ) -> None:
        """_summary_

        Args:
            regions_count (int): _description_
            states_count (int): _description_
            counties_count (int): _description_
            weights (list[Any]): _description_
            num (int): _description_
            hot_layer_constraint (_type_): _description_
            preload_data (bool, optional): _description_. Defaults to False.
        """
        self.regions_count = regions_count
        self.states_count = states_count
        self.counties_count = counties_count
        self.weights = weights
        self.num = num
        self.lru = LRUCache(hot_layer_constraint)
        if preload_data:
            self.load_data()

    def load_dict_from_file(self, filename: str) -> Dict:
        current_dir = Path.cwd()
        data_dicts = (Path(current_dir) / "dictionaries").resolve()
        """Load dictionary from a file."""
        with Path.open(data_dicts / filename, "rb") as f:
            return pickle.load(f)

    def load_data(self) -> None:
        """Load data from the pickled dictionaries."""
        self.regions_data = self.load_dict_from_file("regions_mapping.pkl")
        self.states_data = self.load_dict_from_file("states_mapping.pkl")
        self.counties_data = self.load_dict_from_file("counties_mapping.pkl")

    def fetch_data(self, data: dict, count: int) -> dict[Any, Any]:
        """Fetch a subset of items from a dictionary.

        Args:
            data (dict): Source dictionary.
            count (int): Maximum number of items to retrieve.

        Returns:
            dict: A subset of the dictionary.
        """
        # Since dictionaries are unordered, we'll convert the dictionary to a list of items,
        # take the first 'count' items, and then convert it back to a dictionary.
        return dict(list(data.items())[:count])

    def monte_carlo_simulation(self, num_runs: int) -> float:
        """Execute the Monte Carlo simulation for a specified number of runs using parallel threads.

        Args:
            num_runs (int): _description_

        Returns:
            float: _description_
        """

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            # Use a loop to run the simulation num_runs times
            futures = [executor.submit(self.run_simulation) for _ in range(num_runs)]

            results = []
            for _i, f in enumerate(concurrent.futures.as_completed(futures), 1):
                result = f.result()
                results.append(result)

        total_free_requests = sum(free_requests for free_requests in results)
        average_free_requests = total_free_requests / num_runs

        return average_free_requests

    def run_simulation(self) -> int:
        """Execute the simulation.

        Returns:
            int: Total count of free requests.
        """
        free_requests_count = 0

        # Fetch subset of data
        regions_subset = self.fetch_data(self.regions_data, self.regions_count)
        states_subset = self.fetch_data(self.states_data, self.states_count)
        counties_subset = self.fetch_data(self.counties_data, self.counties_count)

        for _ in range(self.num):
            scale = np.random.choice(["regions", "states", "counties"], p=self.weights)
            if scale == "regions":
                data = regions_subset
            elif scale == "states":
                data = states_subset
            else:
                data = counties_subset
            feature_id = np.random.choice(list(data.keys()))
            landsat_scenes = data[feature_id]

            moved_to_hot = False
            for scene in landsat_scenes:
                if self.lru.get(scene) == -1:
                    moved_to_hot = True
                self.lru.put(scene)

            # Record free requests
            if not moved_to_hot:
                free_requests_count += 1

        return free_requests_count
