import concurrent.futures
from multiprocessing import cpu_count
from typing import Any

import numpy as np
from modules.db_connect import connect  # type: ignore
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

    def load_data(self) -> None:
        """Load data from the region, states, and counties tables."""
        with connect() as conn:
            cursor = conn.cursor()
            self.regions_data = self.fetch_data(
                cursor, "regions_mapping", self.regions_count
            )
            self.states_data = self.fetch_data(
                cursor, "states_mapping", self.states_count
            )
            self.counties_data = self.fetch_data(
                cursor, "counties_mapping", self.counties_count
            )
            cursor.close()

    def fetch_data(self, cursor: Any, table: str, count: int) -> dict[Any, Any]:
        """_summary_

        Args:
            cursor (Any): Connection object
            table (str): Table to execute query against.
            count (int): _description_

        Returns:
            dict: _description_
        """
        query = f"SELECT feature_index, landsat_FIDs FROM {table} ORDER BY feature_index LIMIT %s"
        cursor.execute(query, (count,))
        return {row[0]: row[1].split(",") for row in cursor.fetchall()}

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
        """Execute the simulation

        Returns:
            int: _description_
        """
        with connect() as conn:
            cursor = conn.cursor()
            free_requests_count = 0

            for _ in range(self.num):
                scale = np.random.choice(
                    ["regions", "states", "counties"], p=self.weights
                )
                if scale == "regions":
                    data = self.regions_data
                elif scale == "states":
                    data = self.states_data
                else:
                    data = self.counties_data
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

            cursor.close()
            return free_requests_count
