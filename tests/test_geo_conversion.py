from __future__ import annotations

import importlib.util

import pytest

from fudosan_library.exceptions import GeoDependencyError
from fudosan_library.geo import geojson_to_gdf
from fudosan_library.types import FeatureCollection


SAMPLE_GEOJSON: FeatureCollection = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [139.6917, 35.6895]},
            "properties": {"name": "Shinjuku"},
        }
    ],
}


def test_geojson_to_gdf_requires_optional_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str, *args, **kwargs):
        if name == "geopandas":
            return None
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    with pytest.raises(GeoDependencyError):
        geojson_to_gdf(SAMPLE_GEOJSON)


def test_geojson_to_gdf_success_roundtrip() -> None:
    geopandas = pytest.importorskip("geopandas")

    gdf = geojson_to_gdf(SAMPLE_GEOJSON)

    assert len(gdf) == 1
    assert gdf.iloc[0]["name"] == "Shinjuku"
    assert gdf.crs.to_string() == "EPSG:4326"
