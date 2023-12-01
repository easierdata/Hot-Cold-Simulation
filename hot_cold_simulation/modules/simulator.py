import concurrent.futures
import pickle
from multiprocessing import cpu_count
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from modules.lru_cache import LRUCache  # type: ignore
from modules.time_cache import TimeCache


class MonteCarloSimulation:
    def __init__(
        self,
        weights: list[float],
        num: int,
        cache_type,
        param,
        prepopulate_cache: bool = False,
        return_type: str = "requests",
    ) -> None:
        """_summary_

        Args:
            weights (list[Any]): _description_
            num (int): _description_
            hot_layer_constraint (_type_): _description_
            preload_data (bool, optional): _description_. Defaults to False.
        """
        self.weights = weights
        self.num = num
        self.return_type = return_type
        if cache_type == "LRUCache":
            self.cache = LRUCache(param, prepopulate_cache)
        elif cache_type == "TimeCache":
            self.cache = TimeCache(param)
        else:
            raise ValueError("Invalid cache type. Use 'LRUCache' or 'TimeCache'.")
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
                free_requests, _ = f.result()  # Extract only the free_requests_count
                results.append(free_requests)

        total_free_requests = sum(results)
        average_free_requests = total_free_requests / num_runs

        return average_free_requests

    def run_simulation(self) -> Tuple[int, List[Any]]:
        """Execute the simulation.

        Returns:
            Tuple[int, List[Any]]: Tuple containing total count of free requests and history.
        """
        free_scenes = 0
        total_scenes = 0
        free_requests = 0
        history: List[Any] = []

        # Fetch subset of data
        regions_subset = self.fetch_data(self.regions_data, 6)
        states_subset = self.fetch_data(self.states_data, 49)
        counties_subset = self.fetch_data(self.counties_data, 4437)

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
                total_scenes += 1
                if self.cache.get(scene) != -1:
                    moved_to_hot = True
                    free_scenes += 1

            if moved_to_hot:
                free_requests += 1
            self.cache.put(landsat_scenes)
            history.append(self.cache.current_state())

        free_ratio = free_scenes / total_scenes if total_scenes > 0 else 0

        if self.return_type == "ratio":  # type: ignore
            return free_ratio, history  # type: ignore
        elif self.return_type == "requests":  # type: ignore
            return free_requests, history  # type: ignore
        elif self.return_type == "scenes":  # type: ignore
            return free_scenes, history  # type: ignore
        else:
            raise ValueError("Invalid return type specified")
