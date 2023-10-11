# Standard library imports
import os
import time
from os import cpu_count

# Third-party imports
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Custom imports
from modules.monte_carlo_simulation import MonteCarloSimulation
from modules.logger_config import setup_logger
from modules.linear_combinations import linear_combinations

logger = setup_logger('monte_carlo', 'monte_carlo_results')

# hardcoded to avoid unnecessary database query, do not change
regions_count = 6
states_count = 49
counties_count = 4437

# Set your desired parameters here
step_size = 0.05
num_requests = 100
hot_layer_constraint = 250

weights_list = list(linear_combinations(step_size))
total_weights = len(weights_list)
init_time = time.time()

logger.info(f"Analysis Initialized with the following parameters\n")
logger.info(f"Feature Scale Weights Step Size: {step_size}")
logger.info(f"Number of Requests per Simulation: {num_requests}")
logger.info(f"Hot Layer Constraint: {hot_layer_constraint}")
logger.info("------------------------------------------\n")

simulator_results = {}
for idx, weights in enumerate(weights_list, 1):
    start_time = time.time()
    if __name__ == '__main__':
        simulator = MonteCarloSimulation(
            regions_count=regions_count,
            states_count=states_count,
            counties_count=counties_count,
            num=num_requests,
            weights=weights,
            hot_layer_constraint=hot_layer_constraint,
            preload_data=True
        )

        average_free_requests = simulator.monte_carlo_simulation(cpu_count()*3)

        logger.info(f"Starting simulation {idx} of {total_weights} with {cpu_count()*3} runs")
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