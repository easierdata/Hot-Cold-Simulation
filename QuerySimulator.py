from multiprocessing import cpu_count
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
import concurrent.futures
from LRUCache import LRUCache
from db_connect import connect

"""Simulation"""
class QuerySimulator:
    def __init__(self, regions, states, counties, conn, num=100, weights=[0.05, 0.2, 0.75], hot_layer_constraint=100, debug_mode=False):
        self.regions = regions
        self.states = states
        self.counties = counties
        self.conn = conn
        self.num = num
        self.weights = weights
        self.hot_layer_constraint = hot_layer_constraint
        self.lru = LRUCache(self.hot_layer_constraint)
        self.debug_mode = debug_mode

    # MultiThreaded Monte Carlo
    def monte_carlo_simulation(self, num_runs):
        """Execute the Monte Carlo simulation for a specified number of runs using parallel threads."""
        logging.info(f"Starting parallelized Monte Carlo simulation with {num_runs} runs.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            # Use a loop to run the simulation num_runs times
            futures = [executor.submit(self.run_simulation) for _ in range(num_runs)]
            
            results = []
            for i, f in enumerate(concurrent.futures.as_completed(futures), 1):
                result = f.result()
                results.append(result)
                logging.info(f"Completed simulation {i} of {num_runs}")

        total_free_requests = sum(free_requests for _, free_requests in results)
        average_free_requests = total_free_requests / num_runs

        logging.info(f"Finished all simulations. Average Free Requests: {average_free_requests}")
        return average_free_requests


    def run_simulation(self):
          """Execute the simulation."""
          conn = connect()
          self.conn = conn

          history = []
          free_requests_count = 0
          cursor = self.conn.cursor()

          for _ in range(self.num):
              # Randomly choose a scale gdf (like "regions", "states", or "counties")
              scale = np.random.choice(['regions', 'states', 'counties'], p=self.weights)

              if scale == 'regions':
                  feature_gdf = self.regions
                  table = "regions_mapping"
              elif scale == 'states':
                  feature_gdf = self.states
                  table = "states_mapping"
              else:
                  feature_gdf = self.counties
                  table = "counties_mapping"

              # Sample one feature from the chosen gdf
              sample = feature_gdf.sample()
              feature_id = int(sample.index[0])
              if self.debug_mode:
                  print(f"Selected Feature ID: {feature_id} from {scale})")
                  print(f"Feature ID Type: {type(feature_id)}")

              # Fetch the required landsat scenes for the chosen feature
              query = f"SELECT landsat_FIDs FROM {table} WHERE feature_index=%s"  # Change '?' to '%s'
              if self.debug_mode:
                  print(f"Executing Query: {query} with Feature ID: {feature_id}")
              cursor.execute(query, (feature_id,))
              result = cursor.fetchone()

              if result is None:
                  if self.debug_mode:
                      print(f"No results fetched for Feature ID: {feature_id} from {table}")
                  continue

              if not result[0]:
                  if self.debug_mode:
                      print(f"Empty landsat_FIDs for Feature ID: {feature_id} from {table}")
                  continue

              landsat_scenes = result[0].split(',')

              moved_to_hot = False
              for scene in landsat_scenes:
                  if self.lru.get(scene) == -1:
                      moved_to_hot = True
                  self.lru.put(scene)
              if self.debug_mode:
                  print(f"Scale: {scale}")
                  print(f"Feature ID: {feature_id}")
                  print(f"Landsat Scenes: {landsat_scenes}")
                  print(f"LRU Cache State Before: {self.lru.current_state()}")
                  print(f"LRU Cache State After: {self.lru.current_state()}")
                  print(f"Moved to Hot: {moved_to_hot}")
                  print("----")

              # Record history
              if moved_to_hot:
                  history.append(self.lru.current_state())
              else:
                  free_requests_count += 1
          cursor.close()
          self.history, free_requests_count = history, free_requests_count

          conn.close()
          return history, free_requests_count
