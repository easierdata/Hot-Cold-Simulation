import pickle
from pathlib import Path
from typing import Dict, List

import geopandas as gpd  # type: ignore
from modules.config import DATA_DIR  # type: ignore

### Data Import
# usa_states_path = DATA_DIR / "USA_States" / "usa_states.shp"
# usa_states = gpd.read_file(usa_states_path)
# usa_states = usa_states.set_geometry("geometry")

# usa_counties_path = DATA_DIR / "USA_Counties" / "usa_counties.shp"
# usa_counties = gpd.read_file(usa_counties_path)
# usa_counties = usa_counties.set_geometry("geometry")

usa_landsat_path = DATA_DIR / "USA_Landsat" / "usa_landsat.shp"
usa_landsat = gpd.read_file(usa_landsat_path)
usa_landsat = usa_landsat.set_geometry("geometry")

usa_divisions_path = DATA_DIR / "USA_Divisions" / "usa_divisions.shp"
usa_divisions = gpd.read_file(usa_divisions_path)
usa_divisions = usa_divisions.set_geometry("geometry")

current_dir = Path.cwd()
data_dicts = (Path(current_dir) / "dictionaries").resolve()


def create_mapping_dictionary(
    gdf: gpd.GeoDataFrame, landsat_gdf: gpd.GeoDataFrame
) -> Dict[int, List[int]]:
    """Create a mapping dictionary using dataframe indices."""
    mapping_dict = {}

    for idx, row in gdf.iterrows():
        intersecting_landsat = landsat_gdf[
            landsat_gdf.geometry.intersects(row.geometry)
        ]
        landsat_indices = intersecting_landsat.index.to_list()  # type: ignore
        mapping_dict[idx] = landsat_indices

    return mapping_dict


def save_dict_to_file(data_dict: Dict, filename: str) -> None:
    """Save dictionary to a file."""
    with Path.open(data_dicts / filename, "wb") as f:
        pickle.dump(data_dict, f)


def load_dict_from_file(filename: str) -> Dict:
    """Load dictionary from a file."""
    with Path.open(data_dicts / filename, "rb") as f:
        return pickle.load(f)


# Create mapping dictionaries
divisions_mapping = create_mapping_dictionary(usa_divisions, usa_landsat)
# states_mapping = create_mapping_dictionary(usa_states, usa_landsat)
# counties_mapping = create_mapping_dictionary(usa_counties, usa_landsat)
# divisions_mapping = create_mapping_dictionary(usa_divisions, usa_landsat)

# Save dictionaries to files
save_dict_to_file(divisions_mapping, "regions_mapping.pkl")
# save_dict_to_file(states_mapping, "states_mapping.pkl")
# save_dict_to_file(counties_mapping, "counties_mapping.pkl")
# save_dict_to_file(divisions_mapping, "divisions_mapping.pkl")
