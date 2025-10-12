# fudosan-library

Python SDK for the MLIT Real Estate Information Library (不動産情報ライブラリ) API.
It wraps the REST endpoints with typed models, retry handling, and optional GeoPandas utilities.

## Installation

```bash
uv pip install fudosan-library
# With GeoPandas extras
uv pip install fudosan-library[geo]
```

## Quick Start

```python
from fudosan_library import FudosanClient

client = FudosanClient(api_key="YOUR_API_KEY")

# XIT001: Real estate price records (JSON array)
trade_records = client.get_trade_prices(
    year=2023,
    price_classification="01",
    area="13",
    city="13101",
)
for record in trade_records:
    print(record.trade_price, record.prefecture_ja)

# XPT001: Real estate trade points (GeoJSON)
trade_points = client.get_trade_points(
    response_format="geojson",
    z=13,
    x=7450,
    y=3220,
    period_from="20231",
    period_to="20234",
    price_classification="01",
)
print(trade_points["features"][0]["properties"])

# XKT002: Urban planning use zones (GeoJSON)
use_zone = client.get_land_use_zones(
    response_format="geojson",
    z=12,
    x=2100,
    y=1040,
)
print(use_zone["features"][0]["geometry"]["type"])

# Prefecture codes catalog (static)
prefectures = client.list_prefectures()
print(prefectures[0].code, prefectures[0].name_ja)

# Resolve prefecture from free-form address
tokyo = client.resolve_prefecture_from_address("東京都千代田区霞が関2-1-3")
print(tokyo.code, tokyo.name_en)

# Resolve municipality (市区町村) from address
chiyoda = client.resolve_municipality_from_address("東京都千代田区霞が関2-1-3")
print(chiyoda.municipality_code, chiyoda.municipality_name)

# Optional: Convert GeoJSON to GeoDataFrame
from fudosan_library.geo import geojson_to_gdf

gdf = geojson_to_gdf(trade_points)
print(gdf.head())
```

## Development

```bash
uv pip install -e .[dev,geo]
uv run ruff check
uv run mypy --strict src tests
uv run pytest -q
```

## Tests

Contract tests mock HTTP responses via `respx`. Run `uv run pytest -q` for unit tests and coverage enforcement.

## License

MIT
