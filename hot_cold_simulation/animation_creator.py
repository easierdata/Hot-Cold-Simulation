import webbrowser
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


def save_animation(anim, filename_without_extension):
    """Function to save animation in multiple formats."""
    gif_writer = PillowWriter(fps=2)
    anim.save(ANIMATION_DIR / f"{filename_without_extension}.gif", writer=gif_writer)
    logger.info(f"Animation Saved as {filename_without_extension}.gif")

    html_path = ANIMATION_DIR / f"{filename_without_extension}.html"
    anim.save(html_path, writer="html")
    logger.info(f"Animation saved as {filename_without_extension}.html")

    # Save the HTML content
    html_content = anim.to_jshtml()
    with html_path.open("w") as file:
        file.write(html_content)

    # Open the animation in the web browser
    webbrowser.open(f"file://{html_path.resolve()}")


# Data Import
usa_states_path = DATA_DIR / "USA_States" / "usa_states.shp"
usa_states = gpd.read_file(usa_states_path)
usa_states = usa_states.set_geometry("geometry")

usa_landsat_path = DATA_DIR / "USA_Landsat" / "usa_landsat.shp"
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry("geometry")
logger.info("Data Loaded")

# Set your desired parameters here
num_requests = 100
cache_type = "LRUCache"
param = 250
weights = [0.1, 0.4, 0.5]

# Create an instance of the simulator
simulator = MonteCarloSimulation(
    num=num_requests,
    weights=weights,
    cache_type=cache_type,
    param=param,
    prepopulate_cache=True,
)
logger.info("Simulation Initialized with the following parameters\n")
logger.info(f"Cache Type: {cache_type}")
logger.info(f"Weights Array: {weights}")
logger.info(f"Number of Requests: {num_requests}")
logger.info(f"Cache Parameter: {param}")
logger.info("------------------------------------------\n")

# Run the simulation
free_requests, history = simulator.run_simulation()

fig, ax = plt.subplots(figsize=(10, 10))

logger.info("Simulation Complete")


def animate(i: Any) -> List[Artist]:
    """Generate each animation frame."""
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
save_animation(anim, "animation")
