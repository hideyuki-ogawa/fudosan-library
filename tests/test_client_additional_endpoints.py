from __future__ import annotations

import httpx
import pytest
import respx

from fudosan_library.client import FudosanClient
from fudosan_library.models import Prefecture


@respx.mock
def test_get_appraisal_documents_returns_list(client: FudosanClient) -> None:
    route = respx.get("https://api.test/XCT001").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "XCT001",
                "status": "OK",
                "data": [
                    {
                        "appraisalId": "123",
                        "prefectureCode": "13",
                        "municipalityCode": "13101",
                        "appraisalYear": 2023,
                    }
                ],
            },
        )
    )

    documents = client.get_appraisal_documents(year=2023, area="13", city="13101")

    assert route.called
    request = route.calls.last.request
    assert request.url.params == httpx.QueryParams({"year": "2023", "area": "13", "city": "13101"})
    assert isinstance(documents, list)
    assert documents[0]["appraisalId"] == "123"


def test_list_prefectures_returns_all_codes(client: FudosanClient) -> None:
    prefectures = client.list_prefectures()

    assert len(prefectures) == 47
    assert all(isinstance(pref, Prefecture) for pref in prefectures)
    assert prefectures[0].code == "01"
    assert prefectures[-1].name_ja == "沖縄県"


@respx.mock
def test_resolve_municipality_from_japanese_address(client: FudosanClient) -> None:
    respx.get("https://api.test/XIT002").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "XIT002",
                "status": "OK",
                "data": [
                    {
                        "prefectureCode": "13",
                        "municipalityCode": "13101",
                        "municipalityName": "千代田区",
                    },
                    {
                        "prefectureCode": "13",
                        "municipalityCode": "13102",
                        "municipalityName": "中央区",
                    },
                ],
            },
        )
    )

    municipality = client.resolve_municipality_from_address("東京都千代田区霞が関2-1-3")

    assert municipality.municipality_code == "13101"
    assert municipality.municipality_name == "千代田区"


@respx.mock
def test_resolve_municipality_from_english_address(client: FudosanClient) -> None:
    respx.get("https://api.test/XIT002").mock(
        side_effect=[
            httpx.Response(
                status_code=200,
                json={
                    "code": "XIT002",
                    "status": "OK",
                    "data": [
                        {
                            "prefectureCode": "27",
                            "municipalityCode": "27100",
                            "municipalityName": "大阪市",
                        },
                        {
                            "prefectureCode": "27",
                            "municipalityCode": "27140",
                            "municipalityName": "堺市",
                        },
                    ],
                },
            ),
            httpx.Response(
                status_code=200,
                json={
                    "code": "XIT002",
                    "status": "OK",
                    "data": [
                        {
                            "prefectureCode": "27",
                            "municipalityCode": "27100",
                            "municipalityName": "Osaka City",
                        },
                        {
                            "prefectureCode": "27",
                            "municipalityCode": "27140",
                            "municipalityName": "Sakai City",
                        },
                    ],
                },
            ),
        ]
    )

    municipality = client.resolve_municipality_from_address("Osaka Prefecture Osaka-shi Kita Ward")

    assert municipality.municipality_code == "27100"
    assert municipality.municipality_name == "Osaka City"


def test_resolve_municipality_invalid_address(client: FudosanClient) -> None:
    with pytest.raises(ValueError):
        client.resolve_municipality_from_address("Atlantis City")


TILE_METHODS = [
    ("get_land_price_points", "XPT002", {"year": 2023}),
    ("get_planning_area_zones", "XKT001", {}),
    ("get_land_use_zones", "XKT002", {}),
    ("get_location_optimization_plan", "XKT003", {}),
    ("get_elementary_school_districts", "XKT004", {}),
    ("get_junior_high_school_districts", "XKT005", {}),
    ("get_school_facilities", "XKT006", {}),
    ("get_childcare_facilities", "XKT007", {}),
    ("get_medical_facilities", "XKT010", {}),
    ("get_welfare_facilities", "XKT011", {}),
    ("get_population_projection_mesh", "XKT013", {}),
    ("get_fire_prevention_zones", "XKT014", {}),
    ("get_station_passenger_volumes", "XKT015", {}),
    ("get_disaster_risk_areas", "XKT016", {}),
    ("get_library_locations", "XKT017", {}),
    ("get_municipal_facilities", "XKT018", {}),
    ("get_natural_park_areas", "XKT019", {}),
    ("get_large_scale_landfill_maps", "XKT020", {}),
    ("get_landslide_prevention_districts", "XKT021", {}),
    ("get_steep_slope_failure_areas", "XKT022", {}),
    ("get_district_plans", "XKT023", {}),
    ("get_high_utilization_districts", "XKT024", {}),
    ("get_liquefaction_tendency_map", "XKT025", {}),
]


@pytest.mark.parametrize(("method_name", "code", "extra_kwargs"), TILE_METHODS)
@respx.mock
def test_geo_tile_endpoints_return_feature_collection(
    client: FudosanClient, method_name: str, code: str, extra_kwargs: dict[str, object]
) -> None:
    route = respx.get(f"https://api.test/{code}").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"type": "FeatureCollection", "features": []},
        )
    )

    method = getattr(client, method_name)
    collection = method(
        response_format="geojson",
        z=12,
        x=2100,
        y=1040,
        **extra_kwargs,
    )

    assert route.called
    request = route.calls.last.request
    expected_params = {
        "response_format": "geojson",
        "z": "12",
        "x": "2100",
        "y": "1040",
    }
    expected_params.update({key: str(value) for key, value in extra_kwargs.items()})
    assert request.url.params == httpx.QueryParams(expected_params)
    assert collection["type"] == "FeatureCollection"


@respx.mock
def test_geo_tile_endpoints_return_bytes_for_pbf(client: FudosanClient) -> None:
    respx.get("https://api.test/XKT002").mock(
        return_value=httpx.Response(
            status_code=200,
            content=b"fake-pbf-data",
            headers={"Content-Type": "application/x-protobuf"},
        )
    )

    payload = client.get_land_use_zones(
        response_format="pbf",
        z=14,
        x=2380,
        y=1255,
    )

    assert isinstance(payload, bytes)
    assert payload == b"fake-pbf-data"
