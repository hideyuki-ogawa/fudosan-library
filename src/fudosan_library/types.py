from __future__ import annotations

from typing import Dict, Iterable, Mapping, MutableMapping, Protocol, TypedDict, Union

from typing_extensions import Literal, NotRequired

JsonPrimitive = Union[str, int, float, bool, None]
JsonValue = Union[JsonPrimitive, "JsonObject", "JsonArray"]
JsonObject = Dict[str, JsonValue]
JsonArray = Iterable[JsonValue]

PriceClassification = Literal["01", "02"]
LanguageCode = Literal["ja", "en"]
ResponseFormat = Literal["geojson", "pbf"]


class Geometry(TypedDict):
    type: Literal[
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
    ]
    coordinates: JsonValue


class Feature(TypedDict, total=False):
    type: Literal["Feature"]
    geometry: Geometry
    properties: JsonObject
    id: NotRequired[str | int]


class FeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: list[Feature]


QueryValue = Union[str, int, float, bool]
QueryParameters = Mapping[str, QueryValue]
MutableQueryParameters = MutableMapping[str, QueryValue]


class SupportsRequest(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, QueryValue] | None = ...,
        headers: Mapping[str, str] | None = ...,
        json: Mapping[str, JsonValue] | None = ...,
        timeout: float | None = ...,
    ) -> "Response":
        ...


class Response(Protocol):
    @property
    def status_code(self) -> int: ...

    def json(self) -> JsonValue: ...

    @property
    def headers(self) -> Mapping[str, str]: ...
