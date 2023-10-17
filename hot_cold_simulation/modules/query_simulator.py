import logging
from typing import Any, Optional

import geopandas as gpd  # type: ignore
import numpy as np
from modules.lru_cache import LRUCache  # type: ignore

logging.basicConfig(level=logging.INFO)


class SingleSim:
    """Simulation"""

    def __init__(
        self,
        regions: gpd.GeoDataFrame,
        states: gpd.GeoDataFrame,
        counties: gpd.GeoDataFrame,
        conn: Any,
        num: int = 100,
        weights: Optional[list[float]] = None,
        hot_layer_constraint: int = 100,
        debug_mode: bool = False,
    ) -> None:
        """Initialize a SingleSim instance.

        Args:
            regions (gpd.GeoDataFrame): A GeoDataFrame containing region data.
            states (gpd.GeoDataFrame): A GeoDataFrame containing state data.
            counties (gpd.GeoDataFrame): A GeoDataFrame containing county data.
            conn (Any): A database connection object.
            num (int, optional): The number of iterations for the simulation. Defaults to 100.
            weights (List[float], optional): A list of weights for choosing scales. Defaults to [0.05, 0.2, 0.75] if no weights are passed in.
            hot_layer_constraint (int, optional): The constraint for the hot layer. Defaults to 100.
            debug_mode (bool, optional): Whether to enable debug mode. Defaults to False.

        """
        self.regions = regions
        self.states = states
        self.counties = counties
        self.conn = conn
        self.num = num
        if weights is None:
            weights = [0.05, 0.2, 0.75]
        self.weights = weights
        self.hot_layer_constraint = hot_layer_constraint
        self.lru = LRUCache(self.hot_layer_constraint)
        self.debug_mode = debug_mode
        self.history: list[Any] = []
        self.free_requests_count = 0

    def run_simulation(self) -> tuple[list[Any], int]:
        """
        Execute the simulation.

        Returns:
            Tuple[List[Any], int]: A tuple containing a list of simulation history and the count of free requests.
        """
        cursor = self.conn.cursor()

        for _ in range(self.num):
            scale, feature_id, landsat_scenes = self.process_scale(cursor)

            if not landsat_scenes:
                continue

            moved_to_hot = self.process_landsat_scenes(landsat_scenes)

            self.record_history(moved_to_hot)

        cursor.close()

        self.conn.close()
        return self.history, self.free_requests_count

    def process_scale(self, cursor: Any) -> tuple[str, int, list[Any] | Any]:
        """Process the choice of scale and fetch data for the chosen scale.

        Args:
            cursor (Any): A database cursor object.

        Returns:
            tuple[str, int, list | Any]:  A tuple containing the chosen scale, feature ID, and a list of Landsat scenes.
        """
        scale, feature_gdf, table = self.choose_scale_and_features()

        feature_id, landsat_scenes = self.sample_feature_data(
            cursor, scale, table, feature_gdf
        )

        return scale, feature_id, landsat_scenes

    def choose_scale_and_features(
        self,
    ) -> tuple[str, gpd.GeoDataFrame, str,]:
        """Choose the scale and associated feature data.

        Returns:
            Tuple[str, gpd.GeoDataFrame, str]: A tuple containing the chosen scale, feature GeoDataFrame, and database table name.
        """
        scale = np.random.choice(["regions", "states", "counties"], p=self.weights)
        if scale == "regions":
            feature_gdf = self.regions
            table = "regions_mapping"
        elif scale == "states":
            feature_gdf = self.states
            table = "states_mapping"
        else:
            feature_gdf = self.counties
            table = "counties_mapping"
        return scale, feature_gdf, table

    def sample_feature_data(
        self, cursor: Any, scale: str, table: str, feature_gdf: gpd.GeoDataFrame
    ) -> tuple[int, list[Any]] | tuple[int, Any]:
        """Sample feature data and fetch Landsat scenes.

        Args:
            cursor (Any): A database cursor object.
            scale (str): The chosen scale.
            table (str): The database table name.
            feature_gdf (gpd.GeoDataFrame): The GeoDataFrame containing feature data.

        Returns:
            tuple[int, list[Any]] | tuple[int, Any]: A tuple containing the feature ID and a list of Landsat scenes.
        """
        sample = feature_gdf.sample()
        feature_id = int(sample.index[0])
        query = f"SELECT landsat_FIDs FROM {table} WHERE feature_index=%s"
        cursor.execute(query, (feature_id,))
        result = cursor.fetchone()
        if result is None or not result[0]:
            return feature_id, []
        landsat_scenes = result[0].split(",")
        return feature_id, landsat_scenes

    def process_landsat_scenes(self, landsat_scenes: list[Any] | Any) -> bool:
        """Process Landsat scenes and cache them.

        Args:
            landsat_scenes (list[Any] | Any): A list of Landsat scenes.

        Returns:
            bool: Whether any scene was moved to the hot layer.
        """
        moved_to_hot = any(self.lru.get(scene) == -1 for scene in landsat_scenes)
        for scene in landsat_scenes:
            self.lru.put(scene)
        return moved_to_hot

    def record_history(self, moved_to_hot: bool) -> None:
        """
        Record simulation history based on scene movements.

        Args:
            moved_to_hot: Whether any scene was moved to the hot layer.
        """
        if moved_to_hot:
            self.history.append(self.lru.current_state())
        else:
            self.free_requests_count += 1
