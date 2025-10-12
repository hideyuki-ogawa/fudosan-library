from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Union, cast
from unicodedata import normalize

import httpx

from .endpoints import EndpointDefinition, get_endpoint
from .exceptions import (
    AuthError,
    BadRequestError,
    HTTPError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .models import Municipality, Prefecture, TradeRecord
from .prefectures import PREFECTURE_CATALOG
from .types import FeatureCollection, LanguageCode, PriceClassification, ResponseFormat

DEFAULT_BASE_URL = "https://www.reinfolib.mlit.go.jp/ex-api/external"
DEFAULT_TIMEOUT = 15.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 0.5
DEFAULT_BACKOFF_JITTER = 0.3

GeoJSONOrBytes = Union[FeatureCollection, bytes]


class FudosanClient:
    """Synchronous client for the MLIT Real Estate Information Library API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_BASE,
        backoff_jitter: float = DEFAULT_BACKOFF_JITTER,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._backoff_jitter = backoff_jitter
        self._client = client or httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "FudosanClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -- Public API methods -------------------------------------------------

    def get_trade_prices(
        self,
        *,
        year: int,
        price_classification: PriceClassification | None = None,
        quarter: int | None = None,
        area: str | None = None,
        city: str | None = None,
        station: str | None = None,
        language: LanguageCode | None = None,
        **filters: object,
    ) -> List[TradeRecord]:
        """Fetch trade/contract price records (XIT001).

        Parameters
        ----------
        year:
            Four digit year (e.g. 2023).
        price_classification:
            "01" (trade), "02" (contract), or None for both.
        quarter:
            Optional quarter index in 1..4.
        area:
            Prefecture code. Required when city/station omitted.
        city:
            Municipality code. Required when area/station omitted.
        station:
            National station code. Required when area/city omitted.
        language:
            "ja" or "en".
        **filters:
            Additional API filters (e.g. landTypeCode).

        Returns
        -------
        list[TradeRecord]
            Parsed price records as typed models.
        """
        params: Dict[str, str] = {"year": str(year)}
        if quarter is not None:
            if quarter not in {1, 2, 3, 4}:
                raise ValueError("quarter must be between 1 and 4")
            params["quarter"] = str(quarter)
        self._maybe_add_param(params, "priceClassification", price_classification)
        self._maybe_add_param(params, "area", area)
        self._maybe_add_param(params, "city", city)
        self._maybe_add_param(params, "station", station)
        self._maybe_add_param(params, "language", language)
        for key, value in filters.items():
            self._maybe_add_param(params, key, value)

        if not any(key in params for key in ("area", "city", "station")):
            raise ValueError("At least one of area, city, or station must be provided.")

        payload = self._request("XIT001", params)
        items = self._extract_list_payload(payload, endpoint_code="XIT001")
        return [TradeRecord.model_validate(item) for item in items]

    def list_municipalities(
        self,
        *,
        area: str,
        language: LanguageCode | None = None,
    ) -> List[Municipality]:
        """List municipalities inside a prefecture (XIT002).

        Parameters
        ----------
        area:
            Prefecture code (2 digits).
        language:
            Optional "ja" or "en".

        Returns
        -------
        list[Municipality]
            Municipality metadata for the prefecture.
        """
        params: Dict[str, str] = {"area": area}
        self._maybe_add_param(params, "language", language)

        payload = self._request("XIT002", params)
        items = self._extract_list_payload(payload, endpoint_code="XIT002")
        return [Municipality.model_validate(item) for item in items]

    def get_appraisal_documents(
        self,
        *,
        year: int,
        area: str | None = None,
        city: str | None = None,
        language: LanguageCode | None = None,
        **filters: object,
    ) -> List[Mapping[str, Any]]:
        """Fetch appraisal document metadata (XCT001).

        Parameters
        ----------
        year:
            Reference year (latest five years).
        area:
            Optional prefecture code.
        city:
            Optional municipality code.
        language:
            "ja" or "en".
        **filters:
            Additional filters supported by the API.

        Returns
        -------
        list[dict]
            Appraisal document entries.
        """
        params: Dict[str, str] = {"year": str(year)}
        self._maybe_add_param(params, "area", area)
        self._maybe_add_param(params, "city", city)
        self._maybe_add_param(params, "language", language)
        for key, value in filters.items():
            self._maybe_add_param(params, key, value)

        payload = self._request("XCT001", params)
        items = self._extract_list_payload(payload, endpoint_code="XCT001")
        return [dict(item) for item in items]

    def list_prefectures(self) -> List[Prefecture]:
        """Return the prefecture code catalog derived from the official spec."""
        return [Prefecture.model_validate(entry) for entry in PREFECTURE_CATALOG]

    def resolve_prefecture_from_address(self, address: str) -> Prefecture:
        """Infer the prefecture from a human-readable address string."""
        normalized_address = normalize("NFKC", address).strip()
        if not normalized_address:
            raise ValueError("Address must not be empty.")

        prefectures = self.list_prefectures()

        for pref in prefectures:
            if normalized_address.startswith(pref.name_ja):
                return pref

        lower_address = normalized_address.casefold()
        for pref in prefectures:
            name_en = pref.name_en
            candidates = {name_en.casefold()}
            if name_en.endswith(" Prefecture"):
                candidates.add(name_en[:-len(" Prefecture")].casefold())
            if any(lower_address.startswith(candidate) for candidate in candidates):
                return pref

        raise ValueError(f"Unable to resolve prefecture from address: {address!r}")

    def resolve_municipality_from_address(self, address: str) -> Municipality:
        """Infer the municipality (市区町村) from a free-form address."""
        prefecture = self.resolve_prefecture_from_address(address)
        normalized_address = normalize("NFKC", address).strip()

        municipalities = self.list_municipalities(area=prefecture.code)
        match = self._match_municipality_by_name(normalized_address, municipalities)
        if match:
            return match

        municipalities_en = self.list_municipalities(area=prefecture.code, language="en")
        english_address = normalized_address.casefold()
        match = self._match_municipality_by_name(english_address, municipalities_en, casefold=True)
        if match:
            return match

        raise ValueError(f"Unable to resolve municipality from address: {address!r}")

    def get_trade_points(
        self,
        *,
        response_format: ResponseFormat,
        z: int,
        x: int,
        y: int,
        period_from: str,
        period_to: str,
        price_classification: PriceClassification | None = None,
        **filters: object,
    ) -> GeoJSONOrBytes:
        """Fetch trade/contract points (XPT001).

        Parameters mirror the official spec: pass XYZ coordinates, period range, and optional filters.
        Returns a GeoJSON FeatureCollection when `response_format=\"geojson\"`, otherwise raw PBF bytes.
        """
        extras: Dict[str, object] = {
            "from": period_from,
            "to": period_to,
        }
        if price_classification is not None:
            extras["priceClassification"] = price_classification
        extras.update(filters)
        return self._fetch_tile_dataset(
            "XPT001",
            response_format=response_format,
            z=z,
            x=x,
            y=y,
            extra_params=extras,
        )

    def get_land_price_points(
        self,
        *,
        response_format: ResponseFormat,
        z: int,
        x: int,
        y: int,
        year: int,
        price_classification: str | None = None,
        **filters: object,
    ) -> GeoJSONOrBytes:
        """Fetch public land price points (XPT002)."""
        extras: Dict[str, object] = {"year": year}
        if price_classification is not None:
            extras["priceClassification"] = price_classification
        extras.update(filters)
        return self._fetch_tile_dataset(
            "XPT002",
            response_format=response_format,
            z=z,
            x=x,
            y=y,
            extra_params=extras,
        )

    # -- Geo tile wrappers --------------------------------------------------

    def get_planning_area_zones(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve urban planning areas /区域区分 (XKT001)."""
        return self._fetch_tile_dataset("XKT001", response_format, z, x, y, filters)

    def get_land_use_zones(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve land use zones (用途地域, XKT002)."""
        return self._fetch_tile_dataset("XKT002", response_format, z, x, y, filters)

    def get_use_zone(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Compatibility alias for get_land_use_zones."""
        return self.get_land_use_zones(
            response_format=response_format,
            z=z,
            x=x,
            y=y,
            **filters,
        )

    def get_location_optimization_plan(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve location optimization plans (立地適正化計画, XKT003)."""
        return self._fetch_tile_dataset("XKT003", response_format, z, x, y, filters)

    def get_elementary_school_districts(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve elementary school districts (小学校区, XKT004)."""
        return self._fetch_tile_dataset("XKT004", response_format, z, x, y, filters)

    def get_junior_high_school_districts(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve junior high school districts (中学校区, XKT005)."""
        return self._fetch_tile_dataset("XKT005", response_format, z, x, y, filters)

    def get_school_facilities(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve school facilities (学校, XKT006)."""
        return self._fetch_tile_dataset("XKT006", response_format, z, x, y, filters)

    def get_childcare_facilities(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve childcare facilities (保育園・幼稚園等, XKT007)."""
        return self._fetch_tile_dataset("XKT007", response_format, z, x, y, filters)

    def get_medical_facilities(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve medical facilities (医療機関, XKT010)."""
        return self._fetch_tile_dataset("XKT010", response_format, z, x, y, filters)

    def get_welfare_facilities(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve welfare facilities (福祉施設, XKT011)."""
        return self._fetch_tile_dataset("XKT011", response_format, z, x, y, filters)

    def get_population_projection_mesh(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve future population mesh (将来推計人口, XKT013)."""
        return self._fetch_tile_dataset("XKT013", response_format, z, x, y, filters)

    def get_fire_prevention_zones(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve fire/quasi-fire prevention zones (防火・準防火地域, XKT014)."""
        return self._fetch_tile_dataset("XKT014", response_format, z, x, y, filters)

    def get_station_passenger_volumes(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve station passenger volumes (駅別乗降客数, XKT015)."""
        return self._fetch_tile_dataset("XKT015", response_format, z, x, y, filters)

    def get_disaster_risk_areas(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve disaster risk areas (災害危険区域, XKT016)."""
        return self._fetch_tile_dataset("XKT016", response_format, z, x, y, filters)

    def get_library_locations(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve library locations (図書館, XKT017)."""
        return self._fetch_tile_dataset("XKT017", response_format, z, x, y, filters)

    def get_municipal_facilities(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve municipal facilities (市区町村役場・集会施設等, XKT018)."""
        return self._fetch_tile_dataset("XKT018", response_format, z, x, y, filters)

    def get_natural_park_areas(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve natural park areas (自然公園地域, XKT019)."""
        return self._fetch_tile_dataset("XKT019", response_format, z, x, y, filters)

    def get_large_scale_landfill_maps(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve large-scale landfill maps (大規模盛土造成地, XKT020)."""
        return self._fetch_tile_dataset("XKT020", response_format, z, x, y, filters)

    def get_landslide_prevention_districts(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve landslide prevention districts (地すべり防止地区, XKT021)."""
        return self._fetch_tile_dataset("XKT021", response_format, z, x, y, filters)

    def get_steep_slope_failure_areas(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve steep slope failure areas (急傾斜地崩壊危険区域, XKT022)."""
        return self._fetch_tile_dataset("XKT022", response_format, z, x, y, filters)

    def get_district_plans(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve district plans (地区計画, XKT023)."""
        return self._fetch_tile_dataset("XKT023", response_format, z, x, y, filters)

    def get_high_utilization_districts(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve high utilization districts (高度利用地区, XKT024)."""
        return self._fetch_tile_dataset("XKT024", response_format, z, x, y, filters)

    def get_liquefaction_tendency_map(
        self, *, response_format: ResponseFormat, z: int, x: int, y: int, **filters: object
    ) -> GeoJSONOrBytes:
        """Retrieve liquefaction tendency maps (液状化発生傾向図, XKT025)."""
        return self._fetch_tile_dataset("XKT025", response_format, z, x, y, filters)

    # -- Internal helpers ---------------------------------------------------

    def _match_municipality_by_name(
        self,
        address: str,
        municipalities: List[Municipality],
        *,
        casefold: bool = False,
    ) -> Optional[Municipality]:
        haystack = address.casefold() if casefold else address
        matches: List[tuple[int, Municipality]] = []

        for municipality in municipalities:
            name = municipality.municipality_name
            if not name:
                continue

            target_name = name.casefold() if casefold else name
            variations = {target_name}
            if casefold:
                variations.add(target_name.replace(" ", ""))
                replacements = {
                    " city": "-shi",
                    " ward": "-ku",
                    " town": "-cho",
                    " village": "-mura",
                }
                for suffix, replacement in replacements.items():
                    if target_name.endswith(suffix):
                        variations.add(target_name[: -len(suffix)] + replacement)
            for candidate in variations:
                if candidate and candidate in haystack:
                    matches.append((len(candidate), municipality))
                    break

        if matches:
            matches.sort(key=lambda item: item[0], reverse=True)
            return matches[0][1]
        return None

    def _fetch_tile_dataset(
        self,
        endpoint_code: str,
        response_format: ResponseFormat,
        z: int,
        x: int,
        y: int,
        extra_params: Mapping[str, object] | None = None,
    ) -> GeoJSONOrBytes:
        fmt = response_format.lower()
        if fmt not in ("geojson", "pbf"):
            raise ValueError("response_format must be 'geojson' or 'pbf'")

        params: Dict[str, str] = {
            "response_format": fmt,
            "z": str(z),
            "x": str(x),
            "y": str(y),
        }
        if extra_params:
            for key, value in extra_params.items():
                self._maybe_add_param(params, key, value)

        expect_json = fmt == "geojson"
        accept_header = "application/json" if expect_json else "application/x-protobuf"
        payload = self._request(
            endpoint_code,
            params,
            expect_json=expect_json,
            headers={"Accept": accept_header},
        )

        if expect_json:
            if not isinstance(payload, Mapping):
                raise ValueError(f"Endpoint {endpoint_code} expected a JSON object response.")
            return self._extract_geojson(payload, endpoint_code=endpoint_code)

        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, bytearray):
            return bytes(payload)
        raise ValueError(f"Endpoint {endpoint_code} returned unexpected binary payload.")

    def _maybe_add_param(self, params: Dict[str, str], key: str, value: object | None) -> None:
        if value is None:
            return
        params[key] = str(value)

    def _request(
        self,
        endpoint_code: str,
        params: Mapping[str, object],
        *,
        expect_json: bool = True,
        headers: Mapping[str, str] | None = None,
    ) -> Any:
        endpoint = get_endpoint(endpoint_code)
        url = f"{self._base_url}{endpoint.path}"
        request_headers: Dict[str, str] = {
            "Ocp-Apim-Subscription-Key": self._api_key,
        }
        if headers:
            request_headers.update(headers)
        if "Accept" not in request_headers:
            request_headers["Accept"] = "application/json" if expect_json else "application/octet-stream"

        normalized_params = self._normalize_params(params)

        attempt = 0
        while True:
            response = self._client.request(
                endpoint.method,
                url,
                params=normalized_params,
                headers=request_headers,
                timeout=self._timeout,
            )

            if response.status_code < 400:
                if expect_json:
                    return self._parse_json(response)
                return response.content

            if self._should_retry(response.status_code) and attempt < self._max_retries:
                attempt += 1
                time.sleep(self._backoff_duration(attempt))
                continue

            self._raise_for_status(response, endpoint)

    def _normalize_params(self, params: Mapping[str, object]) -> Dict[str, str]:
        return {key: str(value) for key, value in params.items()}

    def _should_retry(self, status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code < 600

    def _backoff_duration(self, attempt: int) -> float:
        base = self._backoff_factor * (2 ** (attempt - 1))
        jitter = random.uniform(0, self._backoff_jitter)
        return base + jitter

    def _raise_for_status(self, response: httpx.Response, endpoint: EndpointDefinition) -> None:
        message = self._extract_error_message(response)
        status = response.status_code
        if status == 400:
            raise BadRequestError(status, message, endpoint.code)
        if status == 401:
            raise AuthError(status, message, endpoint.code)
        if status == 404:
            raise NotFoundError(status, message, endpoint.code)
        if status == 429:
            raise RateLimitError(status, message, endpoint.code)
        if 500 <= status < 600:
            raise ServerError(status, message, endpoint.code)
        raise HTTPError(status, message, endpoint.code)

    def _parse_json(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise ValueError("API response is not valid JSON.") from exc

    def _extract_list_payload(
        self,
        payload: Any,
        *,
        endpoint_code: str,
    ) -> List[Mapping[str, Any]]:
        if isinstance(payload, list):
            return [cast(Mapping[str, Any], item) for item in payload]
        if isinstance(payload, Mapping):
            data = payload.get("data")
            if isinstance(data, list):
                return [cast(Mapping[str, Any], item) for item in data]
        raise ValueError(f"Endpoint {endpoint_code} expected a list payload.")

    def _extract_geojson(
        self,
        payload: Mapping[str, Any],
        *,
        endpoint_code: str,
    ) -> FeatureCollection:
        if payload.get("type") == "FeatureCollection":
            features = payload.get("features")
            if isinstance(features, list):
                return {
                    "type": "FeatureCollection",
                    "features": [cast(Mapping[str, Any], feature) for feature in features],
                }

        data = payload.get("data")
        if isinstance(data, Mapping):
            return self._extract_geojson(cast(Mapping[str, Any], data), endpoint_code=endpoint_code)

        raise ValueError(f"Endpoint {endpoint_code} expected a GeoJSON FeatureCollection.")

    def _extract_error_message(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except json.JSONDecodeError:
            return response.text or "Unknown error"

        if isinstance(data, Mapping):
            message = data.get("message") or data.get("status") or data.get("error")
            if isinstance(message, str):
                return message
        return "Unknown error"
