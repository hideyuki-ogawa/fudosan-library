from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping


@dataclass(frozen=True)
class EndpointDefinition:
    code: str
    path: str
    method: str = "GET"
    response_key: str | None = "data"
    expects_geojson: bool = False


_ENDPOINTS: Dict[str, EndpointDefinition] = {
    "XIT001": EndpointDefinition(code="XIT001", path="/XIT001"),
    "XIT002": EndpointDefinition(code="XIT002", path="/XIT002"),
    "XCT001": EndpointDefinition(code="XCT001", path="/XCT001"),
    "XPT001": EndpointDefinition(code="XPT001", path="/XPT001", expects_geojson=True),
    "XPT002": EndpointDefinition(code="XPT002", path="/XPT002", expects_geojson=True),
    "XKT001": EndpointDefinition(code="XKT001", path="/XKT001", expects_geojson=True),
    "XKT002": EndpointDefinition(code="XKT002", path="/XKT002", expects_geojson=True),
    "XKT003": EndpointDefinition(code="XKT003", path="/XKT003", expects_geojson=True),
    "XKT004": EndpointDefinition(code="XKT004", path="/XKT004", expects_geojson=True),
    "XKT005": EndpointDefinition(code="XKT005", path="/XKT005", expects_geojson=True),
    "XKT006": EndpointDefinition(code="XKT006", path="/XKT006", expects_geojson=True),
    "XKT007": EndpointDefinition(code="XKT007", path="/XKT007", expects_geojson=True),
    "XKT010": EndpointDefinition(code="XKT010", path="/XKT010", expects_geojson=True),
    "XKT011": EndpointDefinition(code="XKT011", path="/XKT011", expects_geojson=True),
    "XKT013": EndpointDefinition(code="XKT013", path="/XKT013", expects_geojson=True),
    "XKT014": EndpointDefinition(code="XKT014", path="/XKT014", expects_geojson=True),
    "XKT015": EndpointDefinition(code="XKT015", path="/XKT015", expects_geojson=True),
    "XKT016": EndpointDefinition(code="XKT016", path="/XKT016", expects_geojson=True),
    "XKT017": EndpointDefinition(code="XKT017", path="/XKT017", expects_geojson=True),
    "XKT018": EndpointDefinition(code="XKT018", path="/XKT018", expects_geojson=True),
    "XKT019": EndpointDefinition(code="XKT019", path="/XKT019", expects_geojson=True),
    "XKT020": EndpointDefinition(code="XKT020", path="/XKT020", expects_geojson=True),
    "XKT021": EndpointDefinition(code="XKT021", path="/XKT021", expects_geojson=True),
    "XKT022": EndpointDefinition(code="XKT022", path="/XKT022", expects_geojson=True),
    "XKT023": EndpointDefinition(code="XKT023", path="/XKT023", expects_geojson=True),
    "XKT024": EndpointDefinition(code="XKT024", path="/XKT024", expects_geojson=True),
    "XKT025": EndpointDefinition(code="XKT025", path="/XKT025", expects_geojson=True),
}


def get_endpoint(code: str) -> EndpointDefinition:
    try:
        return _ENDPOINTS[code]
    except KeyError as exc:
        raise KeyError(f"Unknown endpoint code: {code}") from exc


def list_endpoints() -> Mapping[str, EndpointDefinition]:
    return _ENDPOINTS.copy()
