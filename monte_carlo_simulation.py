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
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Custom imports
from QuerySimulator import QuerySimulator
from db_connect import connect

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

""" Weights Analysis """
simulator_results = {}
step_size = 0.02
weights_list = list(linear_combinations(step_size))
total_weights = len(weights_list)
print(f"For step size {step_size}, there are {total_weights} combinations.\n")

for idx, weights in enumerate(weights_list, 1):
    print(f"Running simulation {idx} out of {total_weights} for weights {weights}...")
    
    start_time = time.time()

    conn = connect()
    if __name__ == '__main__':
        simulator = QuerySimulator(usa_regions, usa_states, usa_counties, conn, num=100, weights=weights, hot_layer_constraint=250)
        average_free_requests = simulator.monte_carlo_simulation(8)
    simulator_results[tuple(weights)] = average_free_requests
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Finished simulation {idx}. Average Free Requests: {average_free_requests}\n")
    print(f"Simulation took {elapsed_time:.2f} seconds .\n")

    conn.close()

""" Saving Results"""
df = pd.DataFrame(list(simulator_results.items()), columns=["Weights", "Average Free Requests"])
df.to_csv('results.csv', index=False)

""" Plotting Results """
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