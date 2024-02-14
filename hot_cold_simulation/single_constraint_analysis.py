# Standard library imports
import logging
import sys
import time
from pathlib import Path

import numpy as np

# Third-party imports
from modules.config import MONTE_CARLO_LOG_DIR  # type: ignore
from modules.linear_combinations import linear_combinations  # type: ignore

# Custom imports
from modules.simulator import MonteCarloSimulation  # type: ignore

current_dir = Path.cwd()
monte_carlo_results_dir = (Path(current_dir) / MONTE_CARLO_LOG_DIR).resolve()  # type: ignore


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger that outputs to the console.

    Args:
        name (str): The name of the logger.
        level: The logging level, e.g., logging.INFO, logging.DEBUG.

    Returns:
        Logger: A configured logger instance.
    """
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Set the logging level

    # Create a console handler and set level to debug
    console_handler = logging.StreamHandler(sys.stdout)  # Use sys.stderr if you prefer
    console_handler.setLevel(level)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)

    return logger


logger = setup_logger("Single Simulation")


def run_analysis() -> None:
    """
    This function runs the analysis for the Monte Carlo Simulation.
    """
    num_requests = 100
    weights_list = list(linear_combinations(0.05))
    cache_type = "LRUCache"
    parameter = 215
    init_time = time.time()
    num_runs = 32
    prepopulate_cache = True
    return_type = "requests"

    simulator_results = run_simulation(
        num_requests=num_requests,
        weights_list=weights_list,
        cache_type=cache_type,
        parameter=parameter,
        num_runs=num_runs,
        prepopulate_cache=prepopulate_cache,
        return_type=return_type,
    )
    logger.info(f"Analysis completed in {(time.time() - init_time):.2f} seconds")


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
    parameter,
    num_runs,
    prepopulate_cache,
    return_type,
):
    simulator_results = {}
    start_time = time.time()
    weight_results = {}
    for ijx, weights in enumerate(weights_list, start=1):
        wstart_time = time.time()
        # if __name__ == "__main__":
        simulator = MonteCarloSimulation(
            num=num_requests,
            weights=weights,
            cache_type=cache_type,
            param=parameter,
            prepopulate_cache=prepopulate_cache,
            return_type=return_type,
        )
        results = simulator.monte_carlo_simulation(num_runs)
        average_free_requests = sum(results) / num_runs
        free_request_std = np.std(np.array(results))
        weight_results[tuple(weights)] = average_free_requests

        logger.info(
            f"      Weight Analysis {weights} completed in {(time.time() - wstart_time):.2f} seconds"
        )
        logger.info(f"      Mean requests {average_free_requests}")
        logger.info(f"      variance of requests {free_request_std}")
        logger.info("------------------------------------------\n")

    optimal_weights, max_free_requests = calculate_results(weight_results)
    logger.info(f"Optimal weights are: {optimal_weights}")
    logger.info(f"Maximum free requests are: {max_free_requests}")
    logger.info("------------------------------------------\n")
    simulator_results = [optimal_weights, max_free_requests]

    return simulator_results


run_analysis()
