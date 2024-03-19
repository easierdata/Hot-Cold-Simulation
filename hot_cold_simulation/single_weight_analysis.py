# Standard library imports
import logging
import sys
import time
from pathlib import Path

# Third-party imports
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.ticker as ticker
import numpy as np
from modules.config import MONTE_CARLO_LOG_DIR  # type: ignore

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


def run_analysis(weights) -> dict:
    """
    This function runs the analysis for the Monte Carlo Simulation.
    """
    num_requests = 100
    weights = weights
    cache_type = "TimeCache"
    parameters_list = np.linspace(1, 10, 10)
    init_time = time.time()
    num_runs = 100
    prepopulate_cache = True
    return_type = "requests"

    simulator_results = run_simulation(
        num_requests=num_requests,
        weights=weights,
        cache_type=cache_type,
        parameters_list=parameters_list,
        num_runs=num_runs,
        prepopulate_cache=prepopulate_cache,
        return_type=return_type,
    )
    logger.info(f"Analysis completed in {(time.time() - init_time):.2f} seconds")

    return simulator_results  # type: ignore


def run_simulation(
    num_requests,
    weights,
    cache_type,
    parameters_list,
    num_runs,
    prepopulate_cache,
    return_type,
):
    parameter_results = {}
    for ijx, parameter in enumerate(parameters_list, start=1):
        parameter = int(parameter)
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
        free_request_sem = free_request_std / np.sqrt(num_runs)
        parameter_results[parameter] = [average_free_requests, free_request_sem]

        logger.info(
            f"      Parameter Analysis {parameter} completed in {(time.time() - wstart_time):.2f} seconds"
        )
        logger.info(f"      Mean requests {average_free_requests}")
        logger.info(f"      variance of requests {free_request_std}")
        logger.info("------------------------------------------\n")

    logger.info("------------------------------------------\n")

    return parameter_results


def plot_single_sim(weights):
    results = run_analysis(weights)
    x = np.array(list(results.keys())) / 8.6
    values = list(results.values())
    y = np.array([val[0] for val in values])
    yerr = np.array([val[1] for val in values])

    plt.figure(figsize=(10, 6))
    plt.errorbar(
        x,
        y,
        yerr=yerr,
        fmt="o",
        color="b",
        ecolor="lightgray",
        elinewidth=3,
        capsize=5,
        capthick=2,
        markersize=4,
    )
    # Calculate coefficients of the line of best fit
    coefficients = np.polyfit(x, y, 2)  # 1 means linear (degree of the polynomial)
    # Create a polynomial from coefficients, representing the line of best fit
    polynomial = np.poly1d(coefficients)

    # Generate y-values for the line of best fit based on x-values
    y_fit = polynomial(x)
    # Plot the line of best fit
    plt.plot(x, y_fit, "-", color="red")  # '-' specifies a solid line
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean) ** 2)  # Total sum of squares
    ss_res = np.sum((y - y_fit) ** 2)  # Residual sum of squares
    r_squared = 1 - (ss_res / ss_tot)

    # Add R^2 as text on the plot
    plt.text(
        0.05,
        0.95,
        f"$R^2 = {r_squared:.3f}$",
        transform=plt.gca().transAxes,
        fontsize=12,
    )
    plt.xticks(range(0, 100, 5))
    plt.yticks(range(0, 100, 5))
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.title("Even Weight with Order 2 Line of Best Fit")
    plt.ylabel("Percent of Free Requests")
    plt.xlabel("Percent of Hot Layer in Relation to Cold Layer")
    plt.show()


def multiplot_LRU():
    county_result = run_analysis([0, 0, 1])
    state_result = run_analysis([0, 1, 0])
    region_result = run_analysis([1, 0, 0])
    even_result = run_analysis([0.33, 0.33, 0.34])
    x = np.array(list(county_result.keys())) / 8.6
    county_values = list(county_result.values())
    state_values = list(state_result.values())
    region_values = list(region_result.values())
    even_values = list(even_result.values())
    county_y = np.array([val[0] for val in county_values])
    state_y = np.array([val[0] for val in state_values])
    region_y = np.array([val[0] for val in region_values])
    even_y = np.array([val[0] for val in even_values])

    plt.figure(figsize=(10, 6))
    plt.plot(x, county_y, color="blue", label="All County")
    plt.plot(x, state_y, color="red", label="All State")
    plt.plot(x, region_y, color="green", label="All Region")
    plt.plot(x, even_y, color="orange", label="Even Ratio")
    plt.legend()
    plt.title("Request Types Result Comparison")
    plt.ylabel("Percentage of Free Requests")
    plt.xlabel("Percentage of Hot Layer in Relation to Cold Layer")
    plt.xticks(range(0, 100, 5))
    plt.yticks(range(0, 100, 5))
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.show()


def multiplot_Time():
    county_result = run_analysis([0, 0, 1])
    state_result = run_analysis([0, 1, 0])
    region_result = run_analysis([1, 0, 0])
    even_result = run_analysis([0.33, 0.33, 0.34])
    x = np.array(list(county_result.keys()))
    county_values = list(county_result.values())
    state_values = list(state_result.values())
    region_values = list(region_result.values())
    even_values = list(even_result.values())
    county_y = np.array([val[0] for val in county_values])
    state_y = np.array([val[0] for val in state_values])
    region_y = np.array([val[0] for val in region_values])
    even_y = np.array([val[0] for val in even_values])

    plt.figure(figsize=(10, 6))
    plt.plot(x, county_y, color="blue", label="All County")
    plt.plot(x, state_y, color="red", label="All State")
    plt.plot(x, region_y, color="green", label="All Region")
    plt.plot(x, even_y, color="orange", label="Even Ratio")
    plt.legend()
    plt.title("Request Types Result Comparison")
    plt.ylabel("Percentage of Free Requests")
    plt.xlabel("Number of Epochs Each Request Lasts For")
    plt.xticks(range(1, 11, 1))
    plt.yticks(range(0, 100, 5))
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.show()


def multiplot_LRU_Time():
    county_result = run_analysis([0, 0, 1])
    state_result = run_analysis([0, 1, 0])
    region_result = run_analysis([1, 0, 0])
    even_result = run_analysis([0.33, 0.33, 0.34])
    x = np.array(list(county_result.keys())) / 8.6
    county_values = list(county_result.values())
    state_values = list(state_result.values())
    region_values = list(region_result.values())
    even_values = list(even_result.values())
    county_y = np.array([val[0] for val in county_values])
    state_y = np.array([val[0] for val in state_values])
    region_y = np.array([val[0] for val in region_values])
    even_y = np.array([val[0] for val in even_values])

    plt.figure(figsize=(10, 6))
    plt.plot(x, county_y, color="blue", label="All County")
    plt.plot(x, state_y, color="red", label="All State")
    plt.plot(x, region_y, color="green", label="All Region")
    plt.plot(x, even_y, color="orange", label="Even Ratio")
    plt.legend()
    plt.title("Request Types Result Comparison")
    plt.ylabel("Percentage of Free Requests")
    plt.xlabel("Percentage of Hot Layer in Relation to Cold Layer")
    plt.xticks(range(0, 100, 5))
    plt.yticks(range(0, 100, 5))
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.show()


multiplot_Time()
