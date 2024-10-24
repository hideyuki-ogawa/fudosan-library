import pytest
import requests
from unittest.mock import patch
import pandas as pd
import geopandas as gpd
from fudosan_library.base import EstateLibraryBase

@pytest.fixture
def estate_library_base():
    # Fixture to create an instance of EstateLibraryBase with a test API key
    return EstateLibraryBase(api_key="test_api_key")

def test_headers(estate_library_base):
    # Test to check if the headers are set correctly
    assert estate_library_base.headers == {"Ocp-Apim-Subscription-Key": "test_api_key"}

@patch("requests.get")
def test_request_success(mock_get, estate_library_base):
    # Test to check if _request method returns a DataFrame on successful request
    mock_response = {
        "data": [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"}
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    endpoint = "test_endpoint"
    params = {"param1": "value1"}
    df = estate_library_base._request(endpoint, params)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["id", "name"]

@patch("requests.get")
def test_request_failure(mock_get, estate_library_base):
    # Test to check if _request method raises an exception on failed request
    mock_get.return_value.status_code = 404

    endpoint = "test_endpoint"
    params = {"param1": "value1"}

    with pytest.raises(Exception) as excinfo:
        estate_library_base._request(endpoint, params)
    assert "Request failed with status code 404" in str(excinfo.value)

@patch("requests.get")
def test_geo_request_success(mock_get, estate_library_base):
    # Test to check if _geo_request method returns a GeoDataFrame on successful request
    mock_response = {
        "crs": {"properties": {"name": "EPSG:4326"}},
        "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [125.6, 10.1]}, "properties": {"name": "Dinagat Islands"}}
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    endpoint = "test_endpoint"
    params = {"param1": "value1"}
    gdf = estate_library_base._geo_request(endpoint, params)

    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty
    assert list(gdf.columns) == ["geometry", "name"]

@patch("requests.get")
def test_geo_request_failure(mock_get, estate_library_base):
    # Test to check if _geo_request method raises an exception on failed request
    mock_get.return_value.status_code = 404

    endpoint = "test_endpoint"
    params = {"param1": "value1"}

    with pytest.raises(Exception) as excinfo:
        estate_library_base._geo_request(endpoint, params)
    assert "Request failed with status code 404" in str(excinfo.value)

def test_create_tile_gdf(estate_library_base):
    # Test to check if create_tile_gdf method returns a valid GeoDataFrame
    z, x, y = 10, 511, 340
    gdf = estate_library_base.create_tile_gdf(z, x, y)

    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty
    assert list(gdf.columns) == ["geometry", "tile_x", "tile_y", "zoom"]
    assert gdf.iloc[0]["tile_x"] == x
    assert gdf.iloc[0]["tile_y"] == y
    assert gdf.iloc[0]["zoom"] == z