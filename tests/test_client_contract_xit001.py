from __future__ import annotations

import httpx
import pytest
import respx

from fudosan_library.client import FudosanClient
from fudosan_library.exceptions import BadRequestError
from fudosan_library.models import TradeRecord


@respx.mock
def test_get_trade_prices_returns_models(client: FudosanClient) -> None:
    route = respx.get("https://api.test/XIT001").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "code": "XIT001",
                "status": "OK",
                "data": [
                    {
                        "TradePrice": 9800000,
                        "MunicipalityCode": "13101",
                        "Prefecture_ja": "東京都",
                        "Area": 60.5,
                        "PriceClassification": "01",
                    }
                ],
            },
        )
    )

    records = client.get_trade_prices(
        year=2023,
        price_classification="01",
        area="13",
        city="13101",
        language="ja",
    )

    assert route.called
    request = route.calls.last.request
    assert request.headers["Ocp-Apim-Subscription-Key"] == "dummy-key"
    assert request.url.params == httpx.QueryParams(
        {
            "year": "2023",
            "priceClassification": "01",
            "area": "13",
            "city": "13101",
            "language": "ja",
        }
    )

    assert len(records) == 1
    record = records[0]
    assert isinstance(record, TradeRecord)
    assert record.trade_price == 9_800_000
    assert record.municipality_code == "13101"
    assert record.prefecture_ja == "東京都"
    assert record.area == pytest.approx(60.5)


@respx.mock
def test_bad_request_errors_raise(client: FudosanClient) -> None:
    respx.get("https://api.test/XIT001").mock(
        return_value=httpx.Response(
            status_code=400,
            json={"code": "XIT001", "status": "ERROR", "message": "invalid parameters"},
        )
    )

    with pytest.raises(BadRequestError):
        client.get_trade_prices(
            year=2023,
            price_classification="01",
            area="00",
        )
