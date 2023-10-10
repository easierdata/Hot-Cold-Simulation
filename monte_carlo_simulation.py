# Standard library imports
import os
import time
import logging
from os import cpu_count
logging.basicConfig(level=logging.INFO)

# Third-party imports
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Custom imports
from quicksim import simulation
from db_connect import connect

# Create and configure a custom logger
logger = logging.getLogger('monte_carlo_logger')
logger.setLevel(logging.INFO)
logger.propagate = False
formatter = logging.Formatter('%(message)s')

# Create handlers
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(os.path.join(os.getcwd(), 'monte_carlo_results', 'results.log'))
file_handler.setFormatter(formatter)

for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

conn = connect()
def get_count(table_name):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
    return count

regions_count = get_count('regions_mapping')
states_count = get_count('states_mapping')
counties_count = get_count('counties_mapping')

conn.close()

"""Execution"""
#Function to create weights for requests
def linear_combinations(step):
    combinations = []
    for i in np.arange(0, 1+step, step):
        for j in np.arange(0, 1-i+step, step):
            k = 1.0 - i - j
            i_rounded, j_rounded, k_rounded = round(i, 2), round(j, 2), round(k, 2)

            # Check if k_rounded is within valid range and the summation equals 1.0
            if 0 <= k_rounded <= 1 and i_rounded + j_rounded + k_rounded == 1.0:
                combinations.append([i_rounded, j_rounded, k_rounded])

    return combinations

""" Weights Analysis """

# Set Parameters
step_size = 0.1
num_requests = 100
hot_layer_constraint = 250
weights_list = list(linear_combinations(step_size))
total_weights = len(weights_list)
init_time = time.time()

logger.info(f"Analysis Initialized with the following parameters\n")
logger.info(f"Feature Scale Weights Step Size: {step_size}")
logger.info(f"Number of Requests per Simulation: {num_requests}")
logger.info(f"Hot Layer Constraing: {hot_layer_constraint}")
logger.info(f"Analysis Starting at {time.time()}\n")

simulator_results = {}
for idx, weights in enumerate(weights_list, 1):
    start_time = time.time()
    if __name__ == '__main__':
        simulator = simulation(
            regions_count=regions_count,
            states_count=states_count,
            counties_count=counties_count,
            num=num_requests,
            weights=weights,
            hot_layer_constraint=hot_layer_constraint
        )

        average_free_requests = simulator.monte_carlo_simulation(cpu_count())

        logger.info(f"Starting simulation {idx} of {total_weights} with {cpu_count()} runs")
        logger.info(f"Simulation {idx} completed in {(time.time() - start_time):.2f} seconds")
        logger.info(f"Average free requests: {average_free_requests}")
        logger.info("------------------------------------------\n")

    simulator_results[tuple(weights)] = average_free_requests

""" Calculating Results """
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

logger.info(f"Analysis completed in {(time.time() - init_time):.2f} seconds")
logger.info(f"Optimal weights (Region, State, County): {optimal_weights}")
logger.info(f"Maximum average free requests: {max_free_requests}")

""" Plotting Results """
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

"""  Saving Results """
monte_carlo_results_dir = os.path.join(os.getcwd(), 'monte_carlo_results')

df = pd.DataFrame(list(simulator_results.items()), columns=["Weights", "Average Free Requests"])
results_csv_path = os.path.join(monte_carlo_results_dir, 'results.csv')
df.to_csv(results_csv_path, index=False)

""" Saving Plot """
plot_file_path = os.path.join(monte_carlo_results_dir, 'plot.html')
fig.write_html(plot_file_path)