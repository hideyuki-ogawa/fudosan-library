from __future__ import annotations

import httpx
import pytest
import respx

from fudosan_library.client import FudosanClient
from fudosan_library.types import FeatureCollection


@respx.mock
def test_get_trade_points_returns_geojson(client: FudosanClient) -> None:
    feature_collection: FeatureCollection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [139.6917, 35.6895]},
                "properties": {
                    "MunicipalityCode": "13101",
                    "PriceClassification": "01",
                    "TradePrice": 125000000,
                },
            }
        ],
    }
    route = respx.get("https://api.test/XPT001").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "XPT001",
                "status": "OK",
                "data": feature_collection,
            },
        )
    )

    collection = client.get_trade_points(
        response_format="geojson",
        z=13,
        x=7450,
        y=3220,
        period_from="20231",
        period_to="20234",
        price_classification="01",
    )

    assert route.called
    request = route.calls.last.request
    assert request.url.params == httpx.QueryParams(
        {
            "response_format": "geojson",
            "z": "13",
            "x": "7450",
            "y": "3220",
            "from": "20231",
            "to": "20234",
            "priceClassification": "01",
        }
    )

    assert collection["type"] == "FeatureCollection"
    assert len(collection["features"]) == 1
    feature = collection["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert feature["properties"]["TradePrice"] == 125_000_000


@respx.mock
def test_get_trade_points_requires_geojson_payload(client: FudosanClient) -> None:
    respx.get("https://api.test/XPT001").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "XPT001",
                "status": "OK",
                "data": {"unexpected": "payload"},
            },
        )
    )

    with pytest.raises(ValueError):
        client.get_trade_points(
            response_format="geojson",
            z=13,
            x=7450,
            y=3220,
            period_from="20231",
            period_to="20234",
        )
