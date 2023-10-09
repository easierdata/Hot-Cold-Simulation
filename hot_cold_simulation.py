## Package Import

# Standard library imports
import os
from collections import OrderedDict
from multiprocessing import cpu_count
import time
import logging

logging.basicConfig(level=logging.INFO)

# Third-party imports
import geopandas as gpd
import psycopg2
import plotly.graph_objects as go
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import PatchCollection
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from scipy.stats import truncnorm
import concurrent.futures

print('Module imports complete')

"""Data Import"""
current_directory = os.path.dirname(os.path.realpath(__file__))

usa_states_path = os.path.join(current_directory, 'data', 'USA_States', 'usa_states.shp')
usa_states = gpd.read_file(usa_states_path)
usa_states = usa_states.set_geometry('geometry')

usa_counties_path = os.path.join(current_directory, 'data', 'USA_Counties', 'usa_counties.shp')
usa_counties = gpd.read_file(usa_counties_path)
usa_counties = usa_counties.set_geometry('geometry')

usa_regions_path = os.path.join(current_directory, 'data', 'USA_Regions', 'usa_regions.shp')
usa_regions = gpd.read_file(usa_regions_path)
usa_regions = usa_regions.set_geometry('geometry')

usa_landsat_path = os.path.join(current_directory, 'data', 'USA_Landsat', 'usa_landsat.shp')
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry('geometry')

print('Data Loaded')

"""PostgreSQL Database Setup for Parallelization"""
DB_NAME = "railway"
DB_USER = "postgres"
DB_PASS = "bfIwUUa1L3RCjGZSw3oX"
DB_HOST = "containers-us-west-179.railway.app"
DB_PORT = "6563"

def connect():
    """Connect to the PostgreSQL database and return the connection."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

"""Hot Layer Data Structure"""
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            # Move the accessed item to the end of the order
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int) -> int:
        # Check if the cache is already full
        if len(self.cache) >= self.capacity:
            # Remove the first item from the cache
            self.cache.popitem(last=False)
        self.cache[key] = key
        return key

    def current_state(self) -> list:
        return list(self.cache.keys())

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


    def monte_carlo_simulation(self, num_runs):
        """Execute the Monte Carlo simulation for a specified number of runs."""
        total_free_requests = 0

        for _ in range(num_runs):
            _, free_requests = self.run_simulation()
            total_free_requests += free_requests

        # Calculate average free requests after all simulations
        average_free_requests = total_free_requests / num_runs
        return average_free_requests

    # MultiProcessing Monte Carlo [BROKEN]
    def multiprocessing_monte_carlo_simulation(self, num_runs):
        """Execute the Monte Carlo simulation for a specified number of runs using parallel threads."""
        logging.info(f"Starting parallelized Monte Carlo simulation with {num_runs} runs.")

        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count()) as executor:
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

    # MultiThreaded Monte Carlo
    def parallelized_monte_carlo_simulation(self, num_runs):
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
          conn = psycopg2.connect(
              dbname=DB_NAME,
              user=DB_USER,
              password=DB_PASS,
              host=DB_HOST,
              port=DB_PORT
          )
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

"""Execution"""
#Function to create weights for requests
def linear_combinations(step=0.05):
    combinations = []
    for i in np.arange(0, 1+step, step):
        for j in np.arange(0, 1-i+step, step):
            k = 1.0 - i - j
            i_rounded, j_rounded, k_rounded = round(i, 2), round(j, 2), round(k, 2)

            # Check if k_rounded is within valid range and the summation equals 1.0
            if 0 <= k_rounded <= 1 and i_rounded + j_rounded + k_rounded == 1.0:
                combinations.append([i_rounded, j_rounded, k_rounded])

    return combinations

print('Functions loaded, Execution Starting')

"""Weights Analysis"""
simulator_results = {}
step_size = 0.1
weights_list = list(linear_combinations(step_size))
total_weights = len(weights_list)
print(f"For step size {step_size}, there are {total_weights} combinations.\n")

for idx, weights in enumerate(weights_list, 1):
    print(f"Running simulation {idx} out of {total_weights} for weights {weights}...")
    
    start_time = time.time()

    conn = connect()
    if __name__ == '__main__':
        simulator = QuerySimulator(usa_regions, usa_states, usa_counties, conn, num=100, weights=weights, hot_layer_constraint=250)
        average_free_requests = simulator.parallelized_monte_carlo_simulation(10)
    simulator_results[tuple(weights)] = average_free_requests
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Finished simulation {idx}. Average Free Requests: {average_free_requests}\n")
    print(f"Simulation took {elapsed_time:.2f} seconds .\n")

    conn.close()

x, y, z, values = [], [], [], []
for weight, avg_free in simulator_results.items():
    x.append(weight[0])
    y.append(weight[1])
    z.append(weight[2])
    values.append(avg_free)

# Find the index of the maximum average free requests
max_index = np.argmax(values)

# Retrieve the corresponding weight combination
optimal_weights = (x[max_index], y[max_index], z[max_index])
max_free_requests = values[max_index]

print(f"Optimal weights (Region, State, County): {optimal_weights}")
print(f"Maximum average free requests: {max_free_requests}")


x, y, z, values = [], [], [], []
for weight, avg_free in simulator_results.items():
    x.append(weight[0])
    y.append(weight[1])
    z.append(weight[2])
    values.append(avg_free)

fig = go.Figure(data=[go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=5,
        color=values,
        colorscale='Viridis',
        opacity=0.8,
        colorbar=dict(title='Average Free Requests')
    )
)])

# Setting the axis titles and z-axis range
fig.update_layout(scene=dict(
        xaxis_title='Region Requests',
        yaxis_title='State Requests',
        zaxis_title='County Requests',
        zaxis=dict(range=[0, 1])  # Setting the z-axis range
    ),
    width=1000,
    height=800,
    margin=dict(r=20, b=10, l=10, t=10)
)

# Display the plot
fig.show()