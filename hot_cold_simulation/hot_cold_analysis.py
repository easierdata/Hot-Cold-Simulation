# Standard library imports
import time
from os import cpu_count, getenv
from pathlib import Path

import dotenv
import numpy as np
import pandas as pd  # type: ignore

# Third-party imports
import plotly.graph_objects as go  # type: ignore
from modules.config import CONFIG_DIR, MONTE_CARLO_LOG_DIR  # type: ignore
from modules.linear_combinations import linear_combinations  # type: ignore
from modules.logger_config import setup_logger  # type: ignore

# Custom imports
from modules.simulator import MonteCarloSimulation  # type: ignore

current_dir = Path.cwd()
monte_carlo_results_dir = (Path(current_dir) / MONTE_CARLO_LOG_DIR).resolve()  # type: ignore
logger = setup_logger(MONTE_CARLO_LOG_DIR)


def run_analysis() -> None:
    """
    This function runs the analysis for the Monte Carlo Simulation.
    """
    (
        num_requests,
        hot_layer_constraint,
        weights_list,
        total_weights,
        init_time,
    ) = load_environment_variables()

    simulator_results = run_simulation(
        num_requests,
        weights_list,
        hot_layer_constraint,
        total_weights,
    )

    (
        optimal_weights,
        max_free_requests,
    ) = calculate_results(simulator_results)

    logger.info(f"Analysis completed in {(time.time() - init_time):.2f} seconds")
    logger.info(f"Optimal weights (Region, State, County): {optimal_weights}")
    logger.info(f"Maximum average free requests: {max_free_requests}")

    plot_results(simulator_results)
    save_results(simulator_results)


def load_environment_variables():
    dotenv.load_dotenv(Path(CONFIG_DIR / "MonteCarlo-Properties.env"))
    step_size = float(getenv("step_size"))  # type: ignore
    num_requests = int(getenv("num_requests"))  # type: ignore
    hot_layer_constraint = int(getenv("hot_layer_constraint"))  # type: ignore
    weights_list = list(linear_combinations(step_size))
    total_weights = len(weights_list)
    init_time = time.time()

    logger.info("Analysis Initialized with the following parameters\n")
    logger.info(f"Feature Scale Weights Step Size: {step_size}")
    logger.info(f"Number of Requests per Simulation: {num_requests}")
    logger.info(f"Hot Layer Constraint: {hot_layer_constraint}")
    logger.info("------------------------------------------\n")

    return (
        num_requests,
        hot_layer_constraint,
        weights_list,
        total_weights,
        init_time,
    )


def order_results(simulator_results):
    x, y, z, values = [], [], [], []
    for weight, avg_free in simulator_results.items():
        x.append(weight[0])
        y.append(weight[1])
        z.append(weight[2])
        values.append(avg_free)

    return x, y, z, values


def calculate_results(simulator_results):
    (
        x,
        y,
        z,
        values,
    ) = order_results(simulator_results)
    # Find the index of the maximum average free requests
    max_index = np.argmax(values)

    # Retrieve the corresponding weight combination
    optimal_weights = (x[max_index], y[max_index], z[max_index])
    max_free_requests = values[max_index]
    return optimal_weights, max_free_requests


def run_simulation(num_requests, weights_list, hot_layer_constraint, total_weights):
    simulator_results = {}
    for idx, weights in enumerate(weights_list, 1):
        start_time = time.time()
        # if __name__ == "__main__":
        simulator = MonteCarloSimulation(
            num=num_requests,
            weights=weights,
            hot_layer_constraint=hot_layer_constraint,
            preload_data=True,
        )

        average_free_requests = simulator.monte_carlo_simulation(cpu_count())  # type: ignore

        logger.info(
            f"Starting simulation {idx} of {total_weights} with {cpu_count()} runs"
        )
        logger.info(
            f"Simulation {idx} completed in {(time.time() - start_time):.2f} seconds"
        )
        logger.info(f"Average free requests: {average_free_requests}")
        logger.info("------------------------------------------\n")

        simulator_results[tuple(weights)] = average_free_requests
    return simulator_results


def plot_results(simulator_results):
    (
        x,
        y,
        z,
        values,
    ) = order_results(simulator_results)
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode="markers",
                marker={
                    "size": 5,
                    "color": values,
                    "colorscale": "Viridis",
                    "opacity": 0.8,
                    "colorbar": {"title": "Average Free Requests"},
                },
            )
        ]
    )

    # Setting the axis titles and z-axis range
    fig.update_layout(
        scene={
            "xaxis_title": "Region Requests",
            "yaxis_title": "State Requests",
            "zaxis_title": "County Requests",
            "zaxis": {"range": [0, 1]},  # Setting the z-axis range
        },
        width=1000,
        height=800,
        margin={"r": 20, "b": 10, "l": 10, "t": 10},
    )

    # Save plot to disk
    plot_file_path = Path(monte_carlo_results_dir / "plot.html")
    fig.write_html(plot_file_path)
    # Display the plot
    fig.show()


def save_results(simulator_results):
    df = pd.DataFrame(
        list(simulator_results.items()), columns=["Weights", "Average Free Requests"]
    )
    results_csv_path = Path(monte_carlo_results_dir / "results.csv")
    df.to_csv(results_csv_path, index=False)


if __name__ == "__main__":
    run_analysis()
