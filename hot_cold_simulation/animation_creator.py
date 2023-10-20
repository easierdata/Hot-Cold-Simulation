import os
import webbrowser
from pathlib import Path
from typing import Any, List

# Third Party Imports
import geopandas as gpd  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.artist import Artist

# Custom Imports
from modules.config import ANIMATION_DIR, DATA_DIR  # type: ignore
from modules.logger_config import setup_logger  # type: ignore
from modules.simulator import MonteCarloSimulation  # type: ignore

logger = setup_logger(ANIMATION_DIR)
# Data Import
usa_states_path = DATA_DIR / "USA_States" / "usa_states.shp"
usa_states = gpd.read_file(usa_states_path)
usa_states = usa_states.set_geometry("geometry")

usa_landsat_path = DATA_DIR / "USA_Landsat" / "usa_landsat.shp"
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry("geometry")
logger.info("Data Loaded")

# hardcoded to avoid unnecessary database query, do not change
regions_count = 6
states_count = 49
counties_count = 4437

# Set your desired parameters here
step_size = 0.025
num_requests = 100
hot_layer_constraint = 250
weights = [0.02, 0.4, 0.58]

# Create an instance of the simulator
simulator = MonteCarloSimulation(
    regions_count=regions_count,
    states_count=states_count,
    counties_count=counties_count,
    num=num_requests,
    weights=weights,
    hot_layer_constraint=hot_layer_constraint,
    preload_data=True,
)
logger.info("Simulation Initialized with the following parameters\n")
logger.info(f"Weights Array: {weights}")
logger.info(f"Number of Requests: {num_requests}")
logger.info(f"Hot Layer Constraint: {hot_layer_constraint}")
logger.info("------------------------------------------\n")

# Run the simulation
free_requests, history = simulator.run_simulation()

fig, ax = plt.subplots(figsize=(10, 10))

logger.info("Simulation Complete")


def animate(i: Any) -> List[Artist]:
    """_summary_

    Args:
        i (Any): _description_
    """
    ax.clear()
    hot_layer_indices = [int(idx) for idx in history[i]]
    hot_layer_gdf = usa_landsat.loc[hot_layer_indices]
    hot_layer_gdf.set_crs(usa_landsat.crs)
    usa_states_plot = usa_states.plot(ax=ax, color="blue", edgecolor="black")
    hot_layer_plot = hot_layer_gdf.plot(ax=ax, color="red", edgecolor="black")
    title_text = ax.set_title(f"Hot Layer State at Query {i + 1}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    ax.set_xlim(-127, -64)
    ax.set_ylim(22, 52)

    # Ensuring the aspect ratio remains equal
    ax.set_aspect("equal", adjustable="box")

    logger.info(f"Frame {i} Generated")
    # Return a list of Artist objects
    return [usa_states_plot, hot_layer_plot, title_text]


anim = FuncAnimation(fig, animate, frames=len(history), repeat=False)

# Save the animation
gif_writer = PillowWriter(fps=2)
anim.save(ANIMATION_DIR / "animation.gif", writer=gif_writer)
logger.info("Animation Saved as gif")
animation_file_path = Path(ANIMATION_DIR / "animation.html").as_posix()
anim.save(animation_file_path, writer="html")

# Save the HTML content
html_content = anim.to_jshtml()
with Path(animation_file_path).open("w") as file:
    file.write(html_content)
logger.info("Animation saved as HTML")

# Open the animation in the web browser
webbrowser.open("file://" + os.path.realpath(animation_file_path))
