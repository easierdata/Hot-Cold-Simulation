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
- [Acknowledgements](#acknowledgements)

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
   regions_count = 6
   states_count = 49
   counties_count = 4437
   step_size = 0.05
   num_requests = 100
   hot_layer_constraint = 250
   ```

2. Run the script:
    ```python
    python main_script.py
    ```
This will generate a 3D plot showing the average free requests for different weight combinations, and save the results and plot to the monte_carlo_results directory.

### Animation Creator: `animation_creator.py`

This script creates an animation showing the state of the hot layer over time as queries are executed.

1. Set the parameters for your simulation in the script:
```python
num = 100  # number of queries
weights = [0.01, 0.24, 0.75]  # weights for region, state, and county respectively
hot_layer_constraint = 250  # maximum number of landsat scenes in the hot layer
debug_mode = True
```

2. Run the script:
```python
python animation_creator.py
```

This will generate an animation showing which landsat scenes are in the hot layer as queries are executed. The animation is saved to the `animation` directory and opened in your web browser.

## Structure

The project is organized into various directories and files, as outlined below:

### Directories:

- `data`: Contains geographical data used in simulations.
- `modules`: A collection of Python scripts that define classes and functions for database connection, caching, and simulation logic.

### Files within `modules` directory:

- `__init__.py`: An empty file that allows the directory to be treated as a package.
- `db_connect.py`: Contains a function to connect to the PostgreSQL database.
- `linear_combinations.py`: Houses a function to generate combinations of feature scale weights based on a specified step size.
- `logger_config.py`: Configures and returns a custom logger for capturing simulation progress and results.
- `lru_cache.py`: Defines a Least Recently Used (LRU) Cache class used for caching data during the simulation.
- `query_simulator.py`: Contains the `QuerySimulator` class for executing a simulation of a series of queries. This simulation method is used for the animation creator.
- `quicksim.py`: Contains the `simulation` class for a streamlined simulation of queries, ultimately allowing for an optimized, multithreaded monte carlo simulation method.

### Main scripts:

- `animation_creator.py`: A script to create animations illustrating the simulation process.
- `database_creator.py`: A script to set up the database used in the simulation.
- `hot_cold_analysis.py`: This script initializes and runs the simulation, calculates results, and generates a 3D scatter plot.

### Configuration files:

- `poetry.lock`, `poetry.toml`, `pyproject.toml`: These files are related to Poetry, a tool for dependency management and packaging in Python. Users can use Poetry to install all necessary dependencies.

### Output directories (created upon execution):

- `animation`: Contains HTML animations visualizing the simulation over time.
- `monte_carlo_results`: Stores CSV files of simulation results, HTML files of 3D scatter plots visualizing the results, and simulation logs.

## Contributing

lorem ipsum

## License

lorem ipsum

## Contact

If you have any questions, comments, or would like to contribute to this project, feel free to reach out:

### My Information

- **Name:** Jack Rickey
- **Email:** jrickey@umd.edu
- **LinkedIn:** [LinkedIn Profile](https://www.linkedin.com/in/jack-rickey/)
- **GitHub:** [GitHub Profile](https://github.com/JRickey)

### My Organization

- **Name:** The Easier Data Initiative
- **Project Lead:** Dr. Taylor Oshan
- **Project Email:** contact@easierdata.org
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
  - [Seth Docherty]() for helping organize and shape this project into production.

- **Organizational Support:**
  - [University of Maryland](https://umd.edu/) for providing the necessary resources and support.
  - [The Smith School of Business](https://www.rhsmith.umd.edu/) for teaching me all that I know about programming in Python.

- **Special Thanks:**
  - I would also like to extend a heartfelt thanks to my close friends, who always pushed me to go further and learn more.

I also appreciate the broader geospatial science community for their continuous engagement and encouragement. Your enthusiasm drives the ongoing improvement of this project.