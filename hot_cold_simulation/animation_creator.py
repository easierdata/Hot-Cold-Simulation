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
from modules.db_connect import connect  # type: ignore
from modules.query_simulator import SingleSim  # type: ignore

# Data Import
usa_states_path = DATA_DIR / "USA_States" / "usa_states.shp"
usa_states = gpd.read_file(usa_states_path)
usa_states = usa_states.set_geometry("geometry")

usa_counties_path = DATA_DIR / "USA_Counties" / "usa_counties.shp"
usa_counties = gpd.read_file(usa_counties_path)
usa_counties = usa_counties.set_geometry("geometry")

usa_regions_path = DATA_DIR / "USA_Regions" / "usa_regions.shp"
usa_regions = gpd.read_file(usa_regions_path)
usa_regions = usa_regions.set_geometry("geometry")

usa_landsat_path = DATA_DIR / "USA_Landsat" / "usa_landsat.shp"
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry("geometry")


# Create an instance of the simulator
conn = connect()
simulator = SingleSim(
    regions=usa_regions,
    states=usa_states,
    counties=usa_counties,
    conn=conn,
    num=100,  # number of queries
    weights=[0.01, 0.24, 0.75],  # weights for region, state, and county respectively
    hot_layer_constraint=250,  # maximum number of landsat scenes in the hot layer
    debug_mode=True,
)

# Run the simulation
history, free_requests = simulator.run_simulation()
conn.close()

fig, ax = plt.subplots(figsize=(10, 10))

minx, miny, maxx, maxy = usa_states.total_bounds


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

    # Return a list of Artist objects
    return [usa_states_plot, hot_layer_plot, title_text]


anim = FuncAnimation(fig, animate, frames=len(history), repeat=False)

# Save the animation
gif_writer = PillowWriter(fps=2)
anim.save(ANIMATION_DIR / "animation.gif", writer=gif_writer)

animation_file_path = Path(ANIMATION_DIR / "animation.html").as_posix()
anim.save(animation_file_path, writer="html")

# Save the HTML content
html_content = anim.to_jshtml()
with Path(animation_file_path).open("w") as file:
    file.write(html_content)

# Open the animation in the web browser
webbrowser.open("file://" + os.path.realpath(animation_file_path))
