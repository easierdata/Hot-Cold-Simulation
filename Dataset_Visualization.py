import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import display, HTML
import geopandas as gpd
from QuerySimulator import QuerySimulator
from db_connect import connect
import webbrowser
print('Loaded Modules')

"""Data Import"""
current_directory = os.path.dirname(os.path.realpath(__file__))

usa_states_path = os.path.join(current_directory, 'data', 'USA_States', 'usa_states.shp')
usa_states = gpd.read_file(usa_states_path)
usa_states = usa_states.set_geometry('geometry')

usa_counties_path = os.path.join(current_directory, 'data', 'USA_Counties', 'usa_counties.shp')
usa_counties = gpd.read_file(usa_counties_path)
usa_counties = usa_counties.set_geometry('geometry')

usa_regions_path = os.path.join(current_directory, 'data', 'USA_Regions', 'usa_regions.shp')
usa_regions = gpd.read_file(usa_regions_path)
usa_regions = usa_regions.set_geometry('geometry')

usa_landsat_path = os.path.join(current_directory, 'data', 'USA_Landsat', 'usa_landsat.shp')
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry('geometry')

print('Loaded Data')

# Create an instance of the simulator
conn = connect()
simulator = QuerySimulator(
    regions=usa_regions,
    states=usa_states,
    counties=usa_counties,
    conn=conn,
    num=100,  # number of queries
    weights=[0.01, 0.24, 0.75],  # weights for region, state, and county respectively
    hot_layer_constraint=250,  # maximum number of landsat scenes in the hot layer
    debug_mode=True
)

# Run the simulation
history, free_requests = simulator.run_simulation()
conn.close()
print(f"Number of free requests: {free_requests}")

fig, ax = plt.subplots(figsize=(10, 10))

def animate(i):
    ax.clear()
    hot_layer_indices = [int(idx) for idx in history[i]]
    hot_layer_gdf = usa_landsat.loc[hot_layer_indices]
    hot_layer_gdf.set_crs(usa_landsat.crs)
    usa_states.plot(ax=ax, color='blue',edgecolor='black')
    hot_layer_gdf.plot(ax=ax, color='red', edgecolor='black')
    ax.set_title(f"Hot Layer State at Query {i + 1}")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

anim = FuncAnimation(fig, animate, frames=len(history), repeat=False)

# Display the animation object
anim.save('animation.html', writer='html')
html_content = anim.to_jshtml()
with open("animation.html", "w") as file:
    file.write(html_content)

webbrowser.open('file://' + os.path.realpath('animation.html'))

