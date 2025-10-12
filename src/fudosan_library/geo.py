from __future__ import annotations

import importlib.util
import json
from typing import Any, Optional

from .exceptions import GeoDependencyError
from .types import FeatureCollection

DEFAULT_CRS = "EPSG:4326"


def _import_geopandas():
    if importlib.util.find_spec("geopandas") is None:
        raise GeoDependencyError()
    import geopandas as gpd  # type: ignore

    return gpd


def _ensure_feature_collection(data: Any) -> FeatureCollection:
    if not isinstance(data, dict):
        raise ValueError("GeoJSON payload must be an object.")
    if data.get("type") != "FeatureCollection":
        raise ValueError("Expected GeoJSON FeatureCollection.")
    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("GeoJSON FeatureCollection requires features list.")
    return {"type": "FeatureCollection", "features": features}


def geojson_to_gdf(
    geojson: FeatureCollection | str,
    *,
    crs: Optional[str] = None,
):
    """Convert a GeoJSON FeatureCollection into a GeoDataFrame."""

    if isinstance(geojson, str):
        data = json.loads(geojson)
    else:
        data = geojson

    feature_collection = _ensure_feature_collection(data)
    geopandas = _import_geopandas()
    crs_value = crs or DEFAULT_CRS
    return geopandas.GeoDataFrame.from_features(feature_collection["features"], crs=crs_value)
