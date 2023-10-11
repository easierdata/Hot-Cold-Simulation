# Third Party Imports
import numpy as np

# Custom Imports
from modules.lru_cache import LRUCache
from modules.db_connect import connect
from modules.logger_config import setup_logger

logger = setup_logger('animation', 'animation')

"""Simulation"""
class SingleSim:
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
                  logger.info(f"Selected Feature ID: {feature_id} from {scale})")
                  logger.info(f"Feature ID Type: {type(feature_id)}")

              # Fetch the required landsat scenes for the chosen feature
              query = f"SELECT landsat_FIDs FROM {table} WHERE feature_index=%s"  # Change '?' to '%s'
              if self.debug_mode:
                  logger.info(f"Executing Query: {query} with Feature ID: {feature_id}")
              cursor.execute(query, (feature_id,))
              result = cursor.fetchone()

              if result is None:
                  if self.debug_mode:
                      logger.info(f"No results fetched for Feature ID: {feature_id} from {table}")
                  continue

              if not result[0]:
                  if self.debug_mode:
                      logger.info(f"Empty landsat_FIDs for Feature ID: {feature_id} from {table}")
                  continue

              landsat_scenes = result[0].split(',')

              moved_to_hot = False
              for scene in landsat_scenes:
                  if self.lru.get(scene) == -1:
                      moved_to_hot = True
                  self.lru.put(scene)
              if self.debug_mode:
                  logger.info(f"Scale: {scale}")
                  logger.info(f"Feature ID: {feature_id}")
                  logger.info(f"Landsat Scenes: {landsat_scenes}")
                  logger.info(f"LRU Cache State Before: {self.lru.current_state()}")
                  logger.info(f"LRU Cache State After: {self.lru.current_state()}")
                  logger.info(f"Moved to Hot: {moved_to_hot}")
                  logger.info("----")

              # Record history
              if moved_to_hot:
                  history.append(self.lru.current_state())
              else:
                  free_requests_count += 1
          cursor.close()
          self.history, free_requests_count = history, free_requests_count

          conn.close()
          return history, free_requests_count
