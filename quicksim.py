from multiprocessing import cpu_count
import numpy as np
import concurrent.futures
from LRUCache import LRUCache
from db_connect import connect

class simulation:
    def __init__(self, regions_count, states_count, counties_count, weights, num, hot_layer_constraint):
        self.regions_count = regions_count
        self.states_count = states_count
        self.counties_count = counties_count
        self.weights = weights
        self.num = num
        self.lru = LRUCache(hot_layer_constraint)

    def monte_carlo_simulation(self, num_runs):
        """Execute the Monte Carlo simulation for a specified number of runs using parallel threads."""

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            # Use a loop to run the simulation num_runs times
            futures = [executor.submit(self.run_simulation) for _ in range(num_runs)]
            
            results = []
            for i, f in enumerate(concurrent.futures.as_completed(futures), 1):
                result = f.result()
                results.append(result)

        total_free_requests = sum(free_requests for free_requests in results)
        average_free_requests = total_free_requests / num_runs

        return average_free_requests

    def run_simulation(self):
        """Execute the simulation."""
        with connect() as conn:
            cursor = conn.cursor()
            free_requests_count = 0

            for _ in range(self.num):
                # Randomly choose a scale
                scale = np.random.choice(['regions', 'states', 'counties'], p=self.weights)

                # Generate a random feature ID based on the scale
                if scale == 'regions':
                    feature_id = np.random.randint(0, self.regions_count)
                    table = "regions_mapping"
                elif scale == 'states':
                    feature_id = np.random.randint(0, self.states_count)
                    table = "states_mapping"
                else:
                    feature_id = np.random.randint(0, self.counties_count)
                    table = "counties_mapping"

                # Fetch the required landsat scenes for the chosen feature
                query = f"SELECT landsat_FIDs FROM {table} WHERE feature_index=%s"
                cursor.execute(query, (feature_id,))
                result = cursor.fetchone()

                landsat_scenes = result[0].split(',')

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
