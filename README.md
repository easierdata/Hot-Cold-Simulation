# Hot-Cold-Simulation

Description:

The Hot-Cold Simulation project aims to simulate and analyze the performance of a cache based decentralized storage system under different weight configurations across three geographical scales - regions, states, and counties. Utilizing a Least Recently Used (LRU) Cache algorithm, the simulation explores how different weight distributions affect the number of free requests achievable before a cache miss occurs, triggering a move to the hot layer of the cache.

By leveraging various Python libraries and a PostgreSQL database, this simulation iteratively tests different weight combinations through a Monte Carlo simulation approach. It logs the average free requests for each weight combination and calculates the optimal weight configuration to achieve the most free requests.

Additionally, the project provides visualization tools to help users better understand the simulation results, including 3D scatter plots and animations showing cache state across queries.

Through this simulation project, users can gain insights into the storage system performance under various scenarios, which could be instrumental in optimizing cache configurations for geospatial data handling in real-world applications.

Purpose:

The primary purpose of the Hot-Cold Simulation project is to provide a systematic approach to understanding and optimizing cache performance for handling geospatial requests at different geographical scales. By determining the optimal weight configurations, it aims to contribute towards more efficient cache management in systems dealing with geospatial data, hence potentially improving response times and reducing computational resources usage.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Structure](#structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. To install all necessary dependencies, follow these steps:

1. Install Poetry if you haven't already:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. Clone the repository:

    ```bash
    git clone https://github.com/your-username/Hot-Cold-Simulation.git
    cd Hot-Cold-Simulation
    ```

3. Install the dependencies:

    ```bash
    poetry install
    ```

## Usage

The project consists of two main scripts: `hot-cold-analysis.py` and `animation_creator.py`. Below are explanations and examples of how to use these scripts.

### Analysis Script: `hot-cold-analysis.py`

This script conducts a Monte Carlo simulation to analyze how different weighting schemes affect the number of free requests in a caching system. The results are then plotted and saved to disk.

1. Set the parameters for your simulation in the script:

   ```python
   step_size = 0.05
   num_requests = 100
   hot_layer_constraint = 250
   ```

   - `step_size` decides how many combinations of weights will be created. More details are available under the linear combinations module in [Structure](#structure).
   - `num_requests` is how many data requests are within one simulation run.
   - `hot_layer_constraint` is the number of how many landsat scenes can be in the hot layer at any given time. The maximum number is 886.

2. Run the script:

    ```python
    python main_script.py
    ```

This will generate a 3D plot showing the average free requests for different weight combinations, and save the results, logs, and plot to the `monte_carlo_results` directory as `results.csv`, `monte_carlo_results.log`, and `plot.html`.

### Animation Creator: `animation_creator.py`

This script creates an animation showing the state of the hot layer over time as queries are executed and save the logs and plot to the `animation` directory. The individual frames of the animation are saved in the `animation_frames` subdirectory.

1. Set the parameters for your simulation in the script:

  ```python
  num = 100
  weights = [0.01, 0.24, 0.75]
  hot_layer_constraint = 250
  debug_mode = True
  ```

- `num` is the number of requests for the simulation.

- `weights` is the probabilities for each scale. The entries correspond to regions, states, and counties respectively. This array must sum to 1 and contain no negative numbers.
- `hot_layer_constraint` is the number of how many landsat scenes can be in the hot layer at any given time. The maximum number is 886.
- `debug_mode` allows for detailed logging of the simulation. Turn this off if you are only interested in the animation.

2. Run the script:

  ```python
  python animation_creator.py
  ```

This will generate an animation showing which landsat scenes are in the hot layer as queries are executed. The animation is saved to the `animation` directory and opened in your web browser. If `debug_mode` is set to `True`, the log is saved to the `animation` directory as `animation_results.log`.

## Structure

The project is organized into various directories and files, as outlined below:

### Directories

- `data`: Contains geographical data used in simulations.
- `modules`: A collection of Python scripts that define classes and functions for database connection, caching, and simulation logic.

### Files within `modules` directory

- `__init__.py`: An empty file that allows the directory to be treated as a package.
- `db_connect.py`: Contains a function to connect to the PostgreSQL database.
- `linear_combinations.py`: Houses a function to generate combinations of feature scale weights based on a specified step size.
- `logger_config.py`: Configures and returns a custom logger for capturing simulation progress and results.
- `lru_cache.py`: Defines a Least Recently Used (LRU) Cache class used for caching data during the simulation.
- `query_simulator.py`: Contains the `QuerySimulator` class for executing a simulation of a series of queries. This simulation method is used for the animation creator.
- `quicksim.py`: Contains the `simulation` class for a streamlined simulation of queries, ultimately allowing for an optimized, multithreaded monte carlo simulation method.

### Main scripts

- `animation_creator.py`: A script to create animations illustrating the simulation process.
- `database_creator.py`: A script to set up the database used in the simulation.
- `hot_cold_analysis.py`: This script initializes and runs the simulation, calculates results, and generates a 3D scatter plot.

### Configuration files

- `poetry.lock`, `poetry.toml`, `pyproject.toml`: These files are related to Poetry, a tool for dependency management and packaging in Python. Users can use Poetry to install all necessary dependencies.

### Output directories (created upon execution)

- `animation`: Contains HTML animations visualizing the simulation over time.
- `monte_carlo_results`: Stores CSV files of simulation results, HTML files of 3D scatter plots visualizing the results, and simulation logs.

## Contributing

lorem ipsum

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

## Contact

If you have any questions, comments, or would like to contribute to this project, feel free to reach out:

### My Information

- **Name:** Jack Rickey
- **Email:** <jrickey@umd.edu>
- **LinkedIn:** [LinkedIn Profile](https://www.linkedin.com/in/jack-rickey/)
- **GitHub:** [GitHub Profile](https://github.com/JRickey)

### My Organization

- **Name:** The Easier Data Initiative
- **Project Lead:** Dr. Taylor Oshan
- **Project Email:** <contact@easierdata.org>
- **Project Website:** [Project Website](https://easierdata.org/)
- **Project LinkedIn:** [Project LinkedIn Page](https://www.linkedin.com/company/easier-data-initiative/)
- **Project Github:** [Project Github Page](https://github.com/easierdata)
- **Project Twitter:**[Project Twitter (X) Profile](https://twitter.com/easierdataorg)

We welcome contributions and feedback!

## Acknowledgments

I would like to extend my heartfelt gratitude to the following individuals and organizations for their support, contributions, and guidance throughout the development of this project:

- **Individual Contributions:**
  - [Dr. Taylor Oshan](https://twitter.com/TaylorOshan) for bringing me on and supporting me throughout this project and many others.
  - [John Solly](https://twitter.com/_jsolly) for guiding me during the early stages of this project.
  - [Seth Docherty](https://github.com/SethDocherty) for helping organize and shape this project into production.

- **Organizational Support:**
  - [University of Maryland](https://umd.edu/) for providing the necessary resources and support.
  - [The Smith School of Business](https://www.rhsmith.umd.edu/) for teaching me all that I know about programming in Python.

- **Special Thanks:**
  - I would also like to extend a heartfelt thanks to my close friends, who always pushed me to go further and learn more.

I also appreciate the broader geospatial science community for their continuous engagement and encouragement. Your enthusiasm drives the ongoing improvement of this project.
