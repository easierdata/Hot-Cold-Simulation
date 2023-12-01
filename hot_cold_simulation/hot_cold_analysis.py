# Standard library imports
import time
from os import getenv
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
        weights_list,
        cache_type,
        param_list,
        total_params,
        init_time,
        num_runs,
        prepopulate_cache,
        return_type,
    ) = load_environment_variables()

    simulator_results = run_simulation(
        num_requests,
        weights_list,
        cache_type,
        param_list,
        total_params,
        num_runs,
        prepopulate_cache,
        return_type=return_type,
    )

    logger.info(f"Analysis completed in {(time.time() - init_time):.2f} seconds")
    plot_bar_chart(simulator_results)


def load_environment_variables():
    dotenv.load_dotenv(Path(CONFIG_DIR / "MonteCarlo-Properties.env"))
    step_size = float(getenv("step_size"))  # type: ignore
    num_requests = int(getenv("num_requests"))  # type: ignore
    cache_type = str(getenv("cache_type"))  # type: ignore
    cache_param_increment = int(getenv("cache_param_increment"))  # type: ignore
    num_runs = int(getenv("num_runs"))  # type: ignore
    prepopulate_cache = bool(getenv("prepopulate_cache"))  # type: ignore
    return_type = str(getenv("return_type"))  # type: ignore

    weights_list = list(linear_combinations(step_size))
    init_time = time.time()

    if cache_type == "LRUCache":
        param_list = list(range(cache_param_increment, 800, cache_param_increment))
    elif cache_type == "TimeCache":
        param_list = list(range(50, 800, cache_param_increment))
    else:
        raise ValueError("Invalid cache type. Use 'LRUCache' or 'TimeCache'.")

    total_params = len(param_list)
    logger.info("Analysis Initialized with the following parameters\n")
    logger.info(f"Cache type {cache_type}")
    logger.info(f"Feature Scale Weights Step Size: {step_size}")
    logger.info(f"Number of Requests per Simulation: {num_requests}")
    logger.info(f"Parameter list {param_list}")
    logger.info("------------------------------------------\n")

    return (
        num_requests,
        weights_list,
        cache_type,
        param_list,
        total_params,
        init_time,
        num_runs,
        prepopulate_cache,
        return_type,
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


def run_simulation(
    num_requests,
    weights_list,
    cache_type,
    param_list,
    total_params,
    num_runs,
    prepopulate_cache,
    return_type,
):
    simulator_results = {}
    for idx, param in enumerate(param_list, start=1):
        start_time = time.time()
        weight_results = {}
        logger.info(f"Starting constraint analysis {idx} of {total_params}")
        for ijx, weights in enumerate(weights_list, start=1):
            wstart_time = time.time()
            # if __name__ == "__main__":
            simulator = MonteCarloSimulation(
                num=num_requests,
                weights=weights,
                cache_type=cache_type,
                param=param,
                prepopulate_cache=prepopulate_cache,
                return_type=return_type,
            )
            average_free_requests = simulator.monte_carlo_simulation(num_runs)  # type: ignore
            weight_results[tuple(weights)] = average_free_requests

            logger.info(
                f"      Weight Analysis {ijx} completed in {(time.time() - wstart_time):.2f} seconds"
            )

        optimal_weights, max_free_requests = calculate_results(weight_results)
        logger.info(
            f"Constraint simulation {idx} completed in {(time.time() - start_time):.2f} seconds"
        )
        logger.info(f"Optimal weights are: {optimal_weights}")
        logger.info(f"Maximum free requests are: {max_free_requests}")
        logger.info("------------------------------------------\n")
        simulator_results[param] = [optimal_weights, max_free_requests]

    return simulator_results


def plot_bar_chart(simulator_results):
    # Extract constraints, weights, and max free requests from results
    constraints = list(simulator_results.keys())
    optimal_weights_list = [result[0] for result in simulator_results.values()]
    max_free_requests_list = [result[1] for result in simulator_results.values()]

    # Create traces for each weight in optimal_weights
    traces = []
    for i in range(3):
        traces.append(  # noqa: PERF401
            go.Bar(
                x=constraints,
                y=[
                    weights[i] * max_free
                    for weights, max_free in zip(
                        optimal_weights_list, max_free_requests_list
                    )
                ],
                name=f"Weight {i+1}",
            )
        )

    # Plot the bar chart
    layout = go.Layout(
        title="Max Free Requests by Constraint",
        barmode="stack",
        xaxis_title="Constraints",
        yaxis_title="Max Free Requests",
    )

    fig = go.Figure(data=traces, layout=layout)
    # Save plot to disk
    plot_file_path = Path(monte_carlo_results_dir / "bar.html")
    fig.write_html(plot_file_path)
    fig.show()


def plot_weight_results(simulator_results):
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


def save_weight_results(simulator_results):
    df = pd.DataFrame(
        list(simulator_results.items()), columns=["Weights", "Average Free Requests"]
    )
    results_csv_path = Path(monte_carlo_results_dir / "results.csv")
    df.to_csv(results_csv_path, index=False)


if __name__ == "__main__":
    run_analysis()
