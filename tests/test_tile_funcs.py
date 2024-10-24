import pytest
from fudosan_library.tile_utils import latlon_to_tile

def test_latlon_to_tile():
    # Test case 1: Equator and Prime Meridian
    zoom, lat, lon = 1, 10, 20
    expected_tile = (zoom, 1, 0)
    assert latlon_to_tile(zoom, lat, lon) == expected_tile

    # Test case 2: Northern Hemisphere
    zoom, lat, lon = 2, 10, 20
    expected_tile = (zoom, 2, 1)
    assert latlon_to_tile(zoom, lat, lon) == expected_tile

    # Test case 3: Southern Hemisphere
    zoom, lat, lon = 1, -10, -20
    expected_tile = (zoom, 0, 1)
    assert latlon_to_tile(zoom, lat, lon) == expected_tile

    # Test case 4: Eastern Hemisphere
    zoom, lat, lon = 2, -10, -20
    expected_tile = (zoom, 1, 2)
    assert latlon_to_tile(zoom, lat, lon) == expected_tile

    # Test case 5: Western Hemisphere
    zoom, lat, lon = 8, 35, 135.8
    expected_tile = (zoom, 224, 101)
    assert latlon_to_tile(zoom, lon, lat) == expected_tile

    # Test case 6: High zoom level
    zoom, lat, lon = 8, 38, -123
    expected_tile = (zoom, 40, 98)
    assert latlon_to_tile(zoom, lon, lat) == expected_tile
