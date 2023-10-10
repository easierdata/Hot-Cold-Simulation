import os
import geopandas as gpd
from db_connect import connect

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


def create_mapping_table_with_list(conn, table_name):
    """Create a mapping table with given name."""
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        feature_index INTEGER PRIMARY KEY,
        landsat_FIDs TEXT
    );
    ''')
    conn.commit()

def populate_table_with_list_mappings_using_index(gdf, landsat_gdf, table_name):
    """Populate the mapping table using dataframe indices."""
    mappings = []

    for idx, row in gdf.iterrows():
        intersecting_landsat = landsat_gdf[landsat_gdf.geometry.intersects(row.geometry)]
        landsat_indices = intersecting_landsat.index.to_list()
        landsat_indices_str = ",".join(map(str, landsat_indices))
        mappings.append((idx, landsat_indices_str))

    with connect() as conn:
        cursor = conn.cursor()
        cursor.executemany(f'''
        INSERT INTO {table_name} (feature_index, landsat_FIDs) VALUES (%s, %s) ON CONFLICT DO NOTHING
        ''', mappings)
        conn.commit()

# Step 1: Connect to the PostgreSQL database and create the tables
conn = connect()
create_mapping_table_with_list(conn, "regions_mapping")
create_mapping_table_with_list(conn, "states_mapping")
create_mapping_table_with_list(conn, "counties_mapping")
conn.close()

# Step 2: Populate the PostgreSQL tables
populate_table_with_list_mappings_using_index(usa_regions, usa_landsat, "regions_mapping")
populate_table_with_list_mappings_using_index(usa_states, usa_landsat, "states_mapping")
populate_table_with_list_mappings_using_index(usa_counties, usa_landsat, "counties_mapping")
